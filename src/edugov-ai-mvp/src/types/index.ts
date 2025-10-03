// Core types for EduGov.AI MVP
export interface User {
  id: string;
  email: string;
  name: string;
  cpf?: string;
  siapeId?: string;
  role: UserRole;
  institution: Institution;
  preferences: UserPreferences;
  createdAt: Date;
  updatedAt: Date;
}

export enum UserRole {
  LEARNER = 'learner',
  INSTRUCTOR = 'instructor',
  ADMIN = 'admin',
  MANAGER = 'manager',
  AUDITOR = 'auditor'
}

export interface Institution {
  id: string;
  name: string;
  type: InstitutionType;
  cnpj: string;
  level: GovernmentLevel;
  region: BrazilianState;
  compliance: ComplianceStatus;
}

export enum InstitutionType {
  FEDERAL = 'federal',
  STATE = 'state',
  MUNICIPAL = 'municipal',
  AUTARCHY = 'autarchy',
  FOUNDATION = 'foundation'
}

export enum GovernmentLevel {
  FEDERAL = 'federal',
  STATE = 'state',
  MUNICIPAL = 'municipal'
}

export enum BrazilianState {
  AC = 'AC', AL = 'AL', AP = 'AP', AM = 'AM', BA = 'BA',
  CE = 'CE', DF = 'DF', ES = 'ES', GO = 'GO', MA = 'MA',
  MT = 'MT', MS = 'MS', MG = 'MG', PA = 'PA', PB = 'PB',
  PR = 'PR', PE = 'PE', PI = 'PI', RJ = 'RJ', RN = 'RN',
  RS = 'RS', RO = 'RO', RR = 'RR', SC = 'SC', SP = 'SP',
  SE = 'SE', TO = 'TO'
}

// Learning Path and Adaptive Engine
export interface LearningPath {
  id: string;
  userId: string;
  courseId: string;
  currentLevel: ProficiencyLevel;
  personalizedContent: Content[];
  adaptiveAssessments: Assessment[];
  progressMetrics: ProgressData;
  estimatedCompletion: Date;
  difficultyAdjustments: DifficultyAdjustment[];
}

export enum ProficiencyLevel {
  BEGINNER = 'beginner',
  ELEMENTARY = 'elementary',
  INTERMEDIATE = 'intermediate',
  UPPER_INTERMEDIATE = 'upper_intermediate',
  ADVANCED = 'advanced',
  PROFICIENT = 'proficient'
}

export interface Content {
  id: string;
  title: string;
  type: ContentType;
  language: LanguageCode;
  difficulty: ProficiencyLevel;
  duration: number; // in minutes
  tags: string[];
  accessibility: AccessibilityFeatures;
  url: string;
  metadata: ContentMetadata;
}

export enum ContentType {
  VIDEO = 'video',
  AUDIO = 'audio',
  TEXT = 'text',
  INTERACTIVE = 'interactive',
  ASSESSMENT = 'assessment',
  SIMULATION = 'simulation'
}

export enum LanguageCode {
  PT_BR = 'pt-BR',
  EN_US = 'en-US',
  ES = 'es',
  FR = 'fr',
  DE = 'de'
}

// Assessment Engine
export interface Assessment {
  id: string;
  courseId: string;
  type: AssessmentType;
  language: LanguageCode;
  questions: Question[];
  timeLimit: number;
  passingScore: number;
  certificationLevel?: CertificationLevel;
  antiCheatingMeasures: SecurityFeature[];
}

export enum AssessmentType {
  DIAGNOSTIC = 'diagnostic',
  FORMATIVE = 'formative',
  SUMMATIVE = 'summative',
  CERTIFICATION = 'certification',
  ADAPTIVE = 'adaptive'
}

export interface Question {
  id: string;
  type: QuestionType;
  content: string;
  options?: string[];
  correctAnswer: string | string[];
  difficulty: ProficiencyLevel;
  tags: string[];
  explanation?: string;
}

export enum QuestionType {
  MULTIPLE_CHOICE = 'multiple_choice',
  TRUE_FALSE = 'true_false',
  FILL_BLANK = 'fill_blank',
  ESSAY = 'essay',
  SPEAKING = 'speaking',
  LISTENING = 'listening'
}

// Government Integration
export interface GovIntegration {
  id: string;
  institutionId: string;
  sintegraConnection: boolean;
  siapeIntegration: boolean;
  lgpdCompliance: ComplianceStatus;
  auditTrail: AuditLog[];
  dataLocalization: DataLocalizationPolicy;
  lastSync: Date;
}

export interface ComplianceStatus {
  isCompliant: boolean;
  lastAudit: Date;
  issues: ComplianceIssue[];
  certifications: string[];
}

export interface AuditLog {
  id: string;
  userId: string;
  action: string;
  resource: string;
  timestamp: Date;
  ip: string;
  userAgent: string;
  details: Record<string, any>;
}

// Analytics and Dashboard
export interface AnalyticsDashboard {
  id: string;
  institutionId: string;
  learnerProgress: ProgressMetrics[];
  institutionMetrics: InstitutionMetrics;
  costEffectiveness: ROIMetrics;
  complianceReports: ComplianceReport[];
  realTimeData: RealTimeMetrics;
}

export interface ProgressMetrics {
  userId: string;
  courseId: string;
  completionRate: number;
  timeSpent: number;
  lastActivity: Date;
  skillProgress: SkillProgress[];
  predictedCompletion: Date;
}

export interface SkillProgress {
  skill: string;
  currentLevel: ProficiencyLevel;
  progress: number;
  targetLevel: ProficiencyLevel;
  estimatedTime: number;
}

// LGPD Compliance
export interface PrivacyControls {
  dataMinimization: boolean;
  consentManagement: ConsentRecord[];
  rightToErasure: DataDeletionPolicy;
  dataPortability: ExportFormat[];
  breachNotification: NotificationProtocol;
}

export interface ConsentRecord {
  userId: string;
  consentType: ConsentType;
  granted: boolean;
  timestamp: Date;
  ipAddress: string;
  version: string;
}

export enum ConsentType {
  DATA_PROCESSING = 'data_processing',
  ANALYTICS = 'analytics',
  MARKETING = 'marketing',
  THIRD_PARTY_SHARING = 'third_party_sharing'
}

// Additional types
export interface UserPreferences {
  language: LanguageCode;
  timezone: string;
  learningStyle: LearningStyle;
  accessibility: AccessibilityPreferences;
  notifications: NotificationPreferences;
}

export enum LearningStyle {
  VISUAL = 'visual',
  AUDITORY = 'auditory',
  KINESTHETIC = 'kinesthetic',
  READING = 'reading'
}

export interface AccessibilityFeatures {
  subtitles: boolean;
  audioDescription: boolean;
  signLanguage: boolean;
  highContrast: boolean;
  largeFonts: boolean;
  keyboardNavigation: boolean;
}

export interface SecurityFeature {
  type: SecurityType;
  enabled: boolean;
  configuration: Record<string, any>;
}

export enum SecurityType {
  PROCTORING = 'proctoring',
  BROWSER_LOCKDOWN = 'browser_lockdown',
  PLAGIARISM_DETECTION = 'plagiarism_detection',
  BIOMETRIC_VERIFICATION = 'biometric_verification'
}

export interface APIResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  metadata?: {
    timestamp: Date;
    requestId: string;
    version: string;
  };
}

// Error types
export class EduGovError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode: number = 500,
    public details?: any
  ) {
    super(message);
    this.name = 'EduGovError';
  }
}

export class ComplianceError extends EduGovError {
  constructor(message: string, details?: any) {
    super(message, 'COMPLIANCE_ERROR', 403, details);
    this.name = 'ComplianceError';
  }
}

export class ValidationError extends EduGovError {
  constructor(message: string, details?: any) {
    super(message, 'VALIDATION_ERROR', 400, details);
    this.name = 'ValidationError';
  }
}