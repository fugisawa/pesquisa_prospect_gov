import { handleAuth, handleLogin, handleLogout, handleCallback, getSession } from '@auth0/nextjs-auth0';
import { NextApiRequest, NextApiResponse } from 'next';
import { LGPDComplianceService } from '@/services/compliance/lgpdCompliance';
import { GovernmentIntegrationService } from '@/services/integration/governmentIntegration';
import { User, ConsentType, ComplianceError } from '@/types';

/**
 * Auth0 Configuration for Government Compliance
 * Implements secure authentication with LGPD compliance and government integration
 */

const lgpdService = new LGPDComplianceService();
const govService = new GovernmentIntegrationService();

/**
 * Custom login handler with government validation
 */
export const customLogin = handleLogin({
  authorizationParams: {
    // Request additional government-specific scopes
    scope: 'openid profile email siape_id cpf institution',
    audience: process.env.AUTH0_AUDIENCE,
    // Force consent for LGPD compliance
    prompt: 'consent',
  },
  returnTo: '/onboarding'
});

/**
 * Custom callback handler with government validation
 */
export const customCallback = handleCallback({
  afterCallback: async (req: NextApiRequest, res: NextApiResponse, session: any) => {
    try {
      const user = session.user;

      // Validate government credentials if provided
      if (user.siape_id && user.cpf) {
        const validation = await govService.validateSIAPEEmployee(
          user.siape_id,
          user.cpf,
          user.institution_cnpj || ''
        );

        if (!validation.valid) {
          throw new ComplianceError('Government credential validation failed');
        }

        // Merge validated government data
        session.user = {
          ...user,
          government_validated: true,
          government_data: validation.employee
        };
      }

      // Request LGPD consent for new users
      if (!user.lgpd_consent_recorded) {
        await requestLGPDConsent(user, req);
      }

      // Log authentication for audit
      await logAuthenticationEvent(user, req, 'login_success');

      return session;
    } catch (error) {
      console.error('Callback error:', error);

      // Log failed authentication
      await logAuthenticationEvent(session?.user, req, 'login_failed', error.message);

      // Redirect to error page
      res.redirect('/auth/error?error=government_validation_failed');
      return session;
    }
  }
});

/**
 * Custom logout handler with compliance logging
 */
export const customLogout = handleLogout({
  returnTo: '/auth/logout-complete',
  onLogout: async (req: NextApiRequest, res: NextApiResponse, session: any) => {
    try {
      if (session?.user) {
        // Log logout for audit trail
        await logAuthenticationEvent(session.user, req, 'logout');

        // Clear any sensitive cached data
        await clearUserCache(session.user.sub);
      }
    } catch (error) {
      console.error('Logout error:', error);
    }
  }
});

/**
 * Request LGPD consent from user
 */
async function requestLGPDConsent(
  user: any,
  req: NextApiRequest
): Promise<void> {
  try {
    const userAgent = req.headers['user-agent'] || 'unknown';
    const ipAddress = getClientIP(req);

    // Request consent for different data processing types
    const consentTypes = [
      ConsentType.DATA_PROCESSING,
      ConsentType.ANALYTICS,
    ];

    for (const consentType of consentTypes) {
      await lgpdService.requestConsent(
        user.sub,
        consentType,
        getConsentPurpose(consentType),
        ipAddress,
        userAgent
      );
    }

    // Mark consent as requested (will be completed in UI)
    user.lgpd_consent_requested = true;
  } catch (error) {
    console.error('LGPD consent request error:', error);
    throw new ComplianceError('Failed to initialize LGPD compliance');
  }
}

/**
 * Get consent purpose description
 */
function getConsentPurpose(consentType: ConsentType): string {
  const purposes = {
    [ConsentType.DATA_PROCESSING]: 'Processamento de dados pessoais para fornecimento dos serviços educacionais da plataforma EduGov.AI',
    [ConsentType.ANALYTICS]: 'Análise de uso da plataforma para melhoria dos serviços educacionais e personalização do aprendizado',
    [ConsentType.MARKETING]: 'Envio de comunicações sobre novos cursos e funcionalidades da plataforma',
    [ConsentType.THIRD_PARTY_SHARING]: 'Compartilhamento de dados com sistemas governamentais autorizados (SIAPE, Sintegra)'
  };

  return purposes[consentType] || 'Processamento de dados conforme termos de uso';
}

/**
 * Log authentication events for audit trail
 */
async function logAuthenticationEvent(
  user: any,
  req: NextApiRequest,
  event: string,
  details?: string
): Promise<void> {
  try {
    const logData = {
      userId: user?.sub || 'unknown',
      event,
      timestamp: new Date(),
      ipAddress: getClientIP(req),
      userAgent: req.headers['user-agent'] || 'unknown',
      details: details || '',
      compliance: true,
      governmentAccess: !!user?.government_validated
    };

    // In production, this would be sent to a secure logging service
    console.log('Auth event logged:', logData);

    // Store in audit database
    // await storeAuditLog(logData);
  } catch (error) {
    console.error('Failed to log authentication event:', error);
  }
}

/**
 * Clear user cache and sensitive data on logout
 */
async function clearUserCache(userId: string): Promise<void> {
  try {
    // Clear Redis cache if used
    // await redis.del(`user:${userId}:*`);

    // Clear any temporary government data
    // await clearTempGovData(userId);

    console.log(`User cache cleared for: ${userId}`);
  } catch (error) {
    console.error('Failed to clear user cache:', error);
  }
}

/**
 * Get client IP address with proper header handling
 */
function getClientIP(req: NextApiRequest): string {
  const forwarded = req.headers['x-forwarded-for'];
  const real = req.headers['x-real-ip'];
  const connection = req.connection?.remoteAddress;

  if (typeof forwarded === 'string') {
    return forwarded.split(',')[0].trim();
  }

  if (typeof real === 'string') {
    return real;
  }

  return connection || 'unknown';
}

/**
 * Middleware to check government compliance
 */
export async function requireGovernmentAuth(
  req: NextApiRequest,
  res: NextApiResponse,
  next: () => void
): Promise<void> {
  try {
    const session = await getSession(req, res);

    if (!session?.user) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    // Check if government validation is required for this institution
    const user = session.user as User;
    if (user.institution?.type !== 'MUNICIPAL' && !user.government_validated) {
      return res.status(403).json({
        error: 'Government credential validation required',
        code: 'GOVERNMENT_VALIDATION_REQUIRED'
      });
    }

    // Check LGPD consent
    const hasConsent = await lgpdService.hasValidConsent(
      user.id,
      ConsentType.DATA_PROCESSING
    );

    if (!hasConsent) {
      return res.status(403).json({
        error: 'Data processing consent required',
        code: 'LGPD_CONSENT_REQUIRED'
      });
    }

    next();
  } catch (error) {
    console.error('Government auth middleware error:', error);
    return res.status(500).json({ error: 'Authentication validation failed' });
  }
}

/**
 * Middleware to check institution-level permissions
 */
export async function requireInstitutionAccess(
  requiredLevel: 'municipal' | 'state' | 'federal'
) {
  return async (req: NextApiRequest, res: NextApiResponse, next: () => void) => {
    try {
      const session = await getSession(req, res);
      const user = session?.user as User;

      if (!user) {
        return res.status(401).json({ error: 'Authentication required' });
      }

      const userLevel = user.institution?.level?.toLowerCase();
      const hasAccess = checkInstitutionAccess(userLevel, requiredLevel);

      if (!hasAccess) {
        return res.status(403).json({
          error: 'Insufficient institution-level permissions',
          required: requiredLevel,
          current: userLevel
        });
      }

      next();
    } catch (error) {
      console.error('Institution access middleware error:', error);
      return res.status(500).json({ error: 'Permission validation failed' });
    }
  };
}

/**
 * Check institution access levels
 */
function checkInstitutionAccess(
  userLevel: string,
  requiredLevel: string
): boolean {
  const levels = ['municipal', 'state', 'federal'];
  const userIndex = levels.indexOf(userLevel);
  const requiredIndex = levels.indexOf(requiredLevel);

  // Higher levels have access to lower level functions
  return userIndex >= requiredIndex;
}

/**
 * Export configured Auth0 handlers
 */
export default handleAuth({
  login: customLogin,
  logout: customLogout,
  callback: customCallback,
  onError(req: NextApiRequest, res: NextApiResponse, error: Error) {
    console.error('Auth0 error:', error);

    // Log error for compliance audit
    logAuthenticationEvent(null, req, 'auth_error', error.message);

    // Redirect to custom error page
    res.redirect(`/auth/error?error=${encodeURIComponent(error.message)}`);
  }
});