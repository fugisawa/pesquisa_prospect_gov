"""
RADAR EDTECH/IDIOMAS - Data Quality Validation Framework
Comprehensive testing suite for prospect research accuracy and completeness
"""

import unittest
import pandas as pd
import requests
import re
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json
import logging
from dataclasses import dataclass
from enum import Enum


class ValidationSeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ValidationResult:
    check_name: str
    passed: bool
    severity: ValidationSeverity
    message: str
    details: Optional[Dict] = None
    affected_records: Optional[List] = None


class DataQualityValidator:
    """Core data quality validation framework for EdTech/Language prospect research"""

    def __init__(self, config: Dict = None):
        self.config = config or {
            'data_freshness_threshold_days': 180,
            'minimum_required_fields': ['company_name', 'sector', 'location', 'website'],
            'website_validation_timeout': 5,
            'duplicate_similarity_threshold': 0.9
        }
        self.logger = logging.getLogger(__name__)
        self.validation_results: List[ValidationResult] = []

    def validate_dataset(self, df: pd.DataFrame) -> Dict:
        """Master validation method - runs all quality checks"""
        self.validation_results = []

        # Core data quality tests
        self._validate_data_completeness(df)
        self._validate_data_freshness(df)
        self._validate_data_consistency(df)
        self._validate_duplicate_detection(df)
        self._validate_business_rules(df)
        self._validate_categorization_accuracy(df)

        # Generate comprehensive report
        return self._generate_validation_report()

    def _validate_data_completeness(self, df: pd.DataFrame):
        """Test 1: Ensure all critical fields are populated"""
        required_fields = self.config['minimum_required_fields']

        for field in required_fields:
            if field not in df.columns:
                self.validation_results.append(ValidationResult(
                    check_name=f"missing_field_{field}",
                    passed=False,
                    severity=ValidationSeverity.CRITICAL,
                    message=f"Required field '{field}' missing from dataset"
                ))
                continue

            # Check for missing values
            missing_count = df[field].isna().sum()
            missing_percentage = (missing_count / len(df)) * 100

            if missing_percentage > 10:  # More than 10% missing
                self.validation_results.append(ValidationResult(
                    check_name=f"completeness_{field}",
                    passed=False,
                    severity=ValidationSeverity.HIGH,
                    message=f"Field '{field}' has {missing_percentage:.1f}% missing values",
                    details={'missing_count': missing_count, 'total_records': len(df)}
                ))
            else:
                self.validation_results.append(ValidationResult(
                    check_name=f"completeness_{field}",
                    passed=True,
                    severity=ValidationSeverity.LOW,
                    message=f"Field '{field}' completeness: {100-missing_percentage:.1f}%"
                ))

    def _validate_data_freshness(self, df: pd.DataFrame):
        """Test 2: Ensure data is recent enough for business decisions"""
        if 'last_updated' not in df.columns:
            self.validation_results.append(ValidationResult(
                check_name="data_freshness",
                passed=False,
                severity=ValidationSeverity.MEDIUM,
                message="No 'last_updated' field found - cannot validate data freshness"
            ))
            return

        threshold_date = datetime.now() - timedelta(days=self.config['data_freshness_threshold_days'])

        # Convert to datetime if needed
        df['last_updated'] = pd.to_datetime(df['last_updated'], errors='coerce')
        old_data_count = (df['last_updated'] < threshold_date).sum()
        old_data_percentage = (old_data_count / len(df)) * 100

        if old_data_percentage > 20:  # More than 20% is old
            self.validation_results.append(ValidationResult(
                check_name="data_freshness",
                passed=False,
                severity=ValidationSeverity.HIGH,
                message=f"{old_data_percentage:.1f}% of data is older than {self.config['data_freshness_threshold_days']} days",
                details={'old_records': old_data_count, 'threshold_days': self.config['data_freshness_threshold_days']}
            ))
        else:
            self.validation_results.append(ValidationResult(
                check_name="data_freshness",
                passed=True,
                severity=ValidationSeverity.LOW,
                message=f"Data freshness: {100-old_data_percentage:.1f}% of records are recent"
            ))

    def _validate_data_consistency(self, df: pd.DataFrame):
        """Test 3: Check for logical consistency in data"""

        # Website format validation
        if 'website' in df.columns:
            website_pattern = re.compile(r'^https?://[^\s/$.?#].[^\s]*$|^[^\s/$.?#].[^\s]*\.[a-z]{2,}$')
            invalid_websites = df[~df['website'].str.match(website_pattern, na=False)]

            if len(invalid_websites) > 0:
                self.validation_results.append(ValidationResult(
                    check_name="website_format",
                    passed=False,
                    severity=ValidationSeverity.MEDIUM,
                    message=f"{len(invalid_websites)} records have invalid website formats",
                    affected_records=invalid_websites.index.tolist()
                ))

        # Employee count consistency
        if 'employee_count' in df.columns and 'company_size' in df.columns:
            inconsistent_size = []
            for idx, row in df.iterrows():
                emp_count = row.get('employee_count', 0)
                size_category = row.get('company_size', '').lower()

                # Business logic: validate size categories match employee counts
                if emp_count and size_category:
                    if (emp_count < 50 and 'large' in size_category) or \
                       (emp_count > 1000 and 'small' in size_category):
                        inconsistent_size.append(idx)

            if inconsistent_size:
                self.validation_results.append(ValidationResult(
                    check_name="size_consistency",
                    passed=False,
                    severity=ValidationSeverity.MEDIUM,
                    message=f"{len(inconsistent_size)} records have inconsistent size categorization",
                    affected_records=inconsistent_size
                ))

    def _validate_duplicate_detection(self, df: pd.DataFrame):
        """Test 4: Identify potential duplicate entries"""
        if 'company_name' not in df.columns:
            return

        # Exact name duplicates
        exact_duplicates = df[df.duplicated(subset=['company_name'], keep=False)]

        if len(exact_duplicates) > 0:
            self.validation_results.append(ValidationResult(
                check_name="exact_duplicates",
                passed=False,
                severity=ValidationSeverity.HIGH,
                message=f"{len(exact_duplicates)} exact duplicate company names found",
                affected_records=exact_duplicates.index.tolist()
            ))

        # Fuzzy matching for similar names
        similar_companies = self._find_similar_company_names(df['company_name'])

        if similar_companies:
            self.validation_results.append(ValidationResult(
                check_name="similar_names",
                passed=False,
                severity=ValidationSeverity.MEDIUM,
                message=f"{len(similar_companies)} pairs of potentially similar company names found",
                details={'similar_pairs': similar_companies}
            ))

    def _validate_business_rules(self, df: pd.DataFrame):
        """Test 5: EdTech/Language sector specific business rules"""

        # Sector validation for EdTech focus
        if 'sector' in df.columns:
            edtech_keywords = ['education', 'edtech', 'e-learning', 'language', 'training', 'learning']
            non_edtech_count = 0

            for idx, row in df.iterrows():
                sector = str(row.get('sector', '')).lower()
                if not any(keyword in sector for keyword in edtech_keywords):
                    non_edtech_count += 1

            if non_edtech_count > len(df) * 0.3:  # More than 30% non-EdTech
                self.validation_results.append(ValidationResult(
                    check_name="sector_relevance",
                    passed=False,
                    severity=ValidationSeverity.HIGH,
                    message=f"{non_edtech_count} companies may not be relevant to EdTech/Language focus",
                    details={'non_edtech_percentage': (non_edtech_count/len(df))*100}
                ))

        # Revenue validation for B2B prospects
        if 'annual_revenue' in df.columns:
            df['annual_revenue'] = pd.to_numeric(df['annual_revenue'], errors='coerce')
            low_revenue_count = (df['annual_revenue'] < 100000).sum()  # Less than $100k

            if low_revenue_count > len(df) * 0.5:  # More than 50% very small
                self.validation_results.append(ValidationResult(
                    check_name="revenue_viability",
                    passed=False,
                    severity=ValidationSeverity.MEDIUM,
                    message=f"{low_revenue_count} companies have very low revenue (< $100k) - may not be viable B2B prospects"
                ))

    def _validate_categorization_accuracy(self, df: pd.DataFrame):
        """Test 6: Validate categorization and scoring accuracy"""

        if 'priority_score' in df.columns:
            df['priority_score'] = pd.to_numeric(df['priority_score'], errors='coerce')

            # Score distribution analysis
            score_distribution = df['priority_score'].describe()

            # Check for reasonable score distribution
            if score_distribution['std'] < 0.5:  # Very low standard deviation
                self.validation_results.append(ValidationResult(
                    check_name="score_distribution",
                    passed=False,
                    severity=ValidationSeverity.MEDIUM,
                    message="Priority scores have very low variance - scoring model may need calibration",
                    details={'std_dev': score_distribution['std']}
                ))

            # Check for extreme outliers
            q1, q3 = df['priority_score'].quantile([0.25, 0.75])
            iqr = q3 - q1
            outliers = df[(df['priority_score'] < q1 - 1.5*iqr) | (df['priority_score'] > q3 + 1.5*iqr)]

            if len(outliers) > len(df) * 0.1:  # More than 10% outliers
                self.validation_results.append(ValidationResult(
                    check_name="score_outliers",
                    passed=False,
                    severity=ValidationSeverity.MEDIUM,
                    message=f"{len(outliers)} priority scores are extreme outliers - review scoring methodology"
                ))

    def _find_similar_company_names(self, names: pd.Series) -> List[Tuple[str, str]]:
        """Find potentially duplicate company names using fuzzy matching"""
        from difflib import SequenceMatcher

        similar_pairs = []
        names_list = names.dropna().unique().tolist()

        for i, name1 in enumerate(names_list):
            for name2 in names_list[i+1:]:
                similarity = SequenceMatcher(None, name1.lower(), name2.lower()).ratio()
                if similarity > self.config['duplicate_similarity_threshold']:
                    similar_pairs.append((name1, name2))

        return similar_pairs

    def _generate_validation_report(self) -> Dict:
        """Generate comprehensive validation report"""
        total_checks = len(self.validation_results)
        passed_checks = sum(1 for result in self.validation_results if result.passed)

        severity_counts = {
            ValidationSeverity.CRITICAL: 0,
            ValidationSeverity.HIGH: 0,
            ValidationSeverity.MEDIUM: 0,
            ValidationSeverity.LOW: 0
        }

        for result in self.validation_results:
            severity_counts[result.severity] += 1

        # Calculate overall quality score
        quality_score = self._calculate_quality_score()

        return {
            'overall_quality_score': quality_score,
            'total_checks': total_checks,
            'passed_checks': passed_checks,
            'failed_checks': total_checks - passed_checks,
            'severity_breakdown': {k.value: v for k, v in severity_counts.items()},
            'detailed_results': [
                {
                    'check': result.check_name,
                    'passed': result.passed,
                    'severity': result.severity.value,
                    'message': result.message,
                    'details': result.details,
                    'affected_records': result.affected_records
                }
                for result in self.validation_results
            ],
            'recommendations': self._generate_recommendations(),
            'validation_timestamp': datetime.now().isoformat()
        }

    def _calculate_quality_score(self) -> float:
        """Calculate overall data quality score (0-100)"""
        if not self.validation_results:
            return 0.0

        # Weight by severity
        severity_weights = {
            ValidationSeverity.CRITICAL: 4,
            ValidationSeverity.HIGH: 3,
            ValidationSeverity.MEDIUM: 2,
            ValidationSeverity.LOW: 1
        }

        total_weight = 0
        weighted_score = 0

        for result in self.validation_results:
            weight = severity_weights[result.severity]
            total_weight += weight
            if result.passed:
                weighted_score += weight

        return (weighted_score / total_weight) * 100 if total_weight > 0 else 0.0

    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations based on validation results"""
        recommendations = []

        critical_failures = [r for r in self.validation_results
                           if not r.passed and r.severity == ValidationSeverity.CRITICAL]

        if critical_failures:
            recommendations.append("🚨 CRITICAL: Address missing required fields before proceeding with analysis")

        high_failures = [r for r in self.validation_results
                        if not r.passed and r.severity == ValidationSeverity.HIGH]

        if high_failures:
            recommendations.append("⚠️ HIGH PRIORITY: Clean duplicate entries and outdated information")

        # Specific recommendations based on failure types
        failed_checks = {r.check_name for r in self.validation_results if not r.passed}

        if 'data_freshness' in failed_checks:
            recommendations.append("📅 Update data sources - significant portion is outdated")

        if 'exact_duplicates' in failed_checks:
            recommendations.append("🔄 Implement deduplication process before analysis")

        if 'sector_relevance' in failed_checks:
            recommendations.append("🎯 Refine targeting criteria to focus on EdTech/Language sector")

        return recommendations


class ValidationTestSuite(unittest.TestCase):
    """Unit tests for the validation framework itself"""

    def setUp(self):
        self.validator = DataQualityValidator()

        # Create sample test data
        self.sample_data = pd.DataFrame({
            'company_name': ['EduTech Solutions', 'Language Learning Inc', 'Tech Corp', 'EduTech Solutions'],
            'sector': ['EdTech', 'Language Learning', 'General Tech', 'EdTech'],
            'location': ['São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'São Paulo'],
            'website': ['https://edutech.com', 'www.language.com', 'invalid-url', 'https://edutech.com'],
            'employee_count': [150, 75, 2000, 150],
            'company_size': ['Medium', 'Small', 'Small', 'Medium'],  # Inconsistent for Tech Corp
            'annual_revenue': [500000, 200000, 50000, 500000],
            'priority_score': [8.5, 7.2, 3.1, 8.5],
            'last_updated': ['2024-01-15', '2024-02-20', '2022-06-10', '2024-01-15']
        })

    def test_duplicate_detection(self):
        """Test duplicate detection functionality"""
        report = self.validator.validate_dataset(self.sample_data)

        # Should detect exact duplicates
        duplicate_results = [r for r in self.validator.validation_results
                           if r.check_name == 'exact_duplicates']
        self.assertTrue(len(duplicate_results) > 0)
        self.assertFalse(duplicate_results[0].passed)

    def test_data_freshness_validation(self):
        """Test data freshness validation"""
        report = self.validator.validate_dataset(self.sample_data)

        freshness_results = [r for r in self.validator.validation_results
                           if r.check_name == 'data_freshness']
        self.assertTrue(len(freshness_results) > 0)

    def test_consistency_validation(self):
        """Test data consistency checks"""
        report = self.validator.validate_dataset(self.sample_data)

        # Should detect website format issues
        website_results = [r for r in self.validator.validation_results
                         if r.check_name == 'website_format']
        self.assertTrue(len(website_results) > 0)

    def test_quality_score_calculation(self):
        """Test quality score calculation"""
        report = self.validator.validate_dataset(self.sample_data)

        self.assertIn('overall_quality_score', report)
        self.assertIsInstance(report['overall_quality_score'], float)
        self.assertGreaterEqual(report['overall_quality_score'], 0)
        self.assertLessEqual(report['overall_quality_score'], 100)


if __name__ == '__main__':
    # Run validation framework tests
    unittest.main()