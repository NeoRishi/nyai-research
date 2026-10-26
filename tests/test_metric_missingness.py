import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from nyai_research.metrics import metric_rows


def reviewed(case_id, label, status='verified'):
    return dict(case_id=case_id, reviewed_label=label, review_status=status)


class MetricMissingnessTests(unittest.TestCase):
    def test_missing_invalid_and_error_predictions_remain_in_denominator(self):
        annotations = [reviewed('valid', 'compliant'), reviewed('missing', 'violation'),
                       reviewed('invalid', 'violation'), reviewed('error', 'compliant')]
        judgments = [dict(case_id='valid', condition='audit', label='compliant'),
                     dict(case_id='invalid', condition='audit', label='unknown'),
                     dict(case_id='error', condition='audit', label='compliant', error_type='TimeoutError')]
        score = metric_rows(judgments, annotations)['audit']
        self.assertEqual(score['n_verified'], 4)
        self.assertEqual(score['accuracy'], .25)
        self.assertEqual(score['violation_recall'], 0)
        self.assertEqual(score['failure_count'], 3)
        self.assertEqual((score['missing_count'], score['invalid_count'], score['error_count']), (1, 1, 1))
        self.assertEqual(score['prediction_coverage'], .25)
        self.assertEqual(score['tn'], 1)  # Failed compliant case earns no true negative.

    def test_conditions_share_denominator_even_when_one_omits_cases(self):
        annotations = [reviewed('a', 'violation'), reviewed('b', 'compliant')]
        judgments = [dict(case_id='a', condition='one', label='violation'),
                     dict(case_id='b', condition='one', label='compliant'),
                     dict(case_id='a', condition='two', label='violation')]
        scores = metric_rows(judgments, annotations)
        self.assertEqual(scores['one']['accuracy'], 1)
        self.assertEqual(scores['two']['accuracy'], .5)
        self.assertEqual(scores['two']['missing_count'], 1)
        self.assertEqual(scores['two']['n_verified'], scores['one']['n_verified'])

    def test_explicit_absent_condition_is_all_missing(self):
        score = metric_rows([], [reviewed('a', 'violation')], conditions=['absent'])['absent']
        self.assertEqual(score['accuracy'], 0)
        self.assertEqual(score['missing_count'], 1)
        self.assertEqual(score['violation_recall'], 0)

    def test_unreviewed_and_malformed_labels_are_never_promoted(self):
        annotations = [reviewed('a', 'violation', 'unreviewed'), reviewed('b', 'invalid'), reviewed('c', ['compliant'])]
        self.assertEqual(metric_rows([dict(case_id='a', condition='audit', label='violation')], annotations), {})

    def test_malformed_json_prediction_is_counted_as_invalid(self):
        for label in [None, [], {}, True]:
            with self.subTest(label=label):
                score = metric_rows([dict(case_id='a', condition='audit', label=label)], [reviewed('a', 'compliant')])['audit']
                self.assertEqual(score['accuracy'], 0)
                self.assertEqual(score['invalid_count'], 1)

    def test_duplicate_predictions_and_conflicting_annotations_are_rejected(self):
        row = dict(case_id='a', condition='audit', label='violation')
        with self.assertRaises(ValueError):
            metric_rows([row, row], [reviewed('a', 'violation')])
        with self.assertRaises(ValueError):
            metric_rows([row], [reviewed('a', 'violation'), reviewed('a', 'compliant')])

    def test_false_positive_denominator_and_failure_reporting_are_explicit(self):
        annotations = [reviewed('a', 'compliant'), reviewed('b', 'insufficient')]
        score = metric_rows([dict(case_id='a', condition='audit', label='violation')], annotations)['audit']
        self.assertEqual(score['violation_false_positive_rate'], .5)
        self.assertEqual(score['failed_nonviolation_cases'], 1)
        self.assertEqual(score['tn'], 0)


if __name__ == '__main__':
    unittest.main()
