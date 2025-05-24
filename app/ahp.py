import numpy as np
from typing import List, Tuple, Dict, Union
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AHPCalculator:
    # Random Index values for matrices of different sizes (1-10)
    RI_VALUES = {
        1: 0.00,
        2: 0.00,
        3: 0.58,
        4: 0.90,
        5: 1.12,
        6: 1.24,
        7: 1.32,
        8: 1.41,
        9: 1.45,
        10: 1.49
    }

    @staticmethod
    def validate_input(value: str) -> float:
        """
        Validate and convert input string to float
        Accepts numbers 1-9 and fractions 1/2-1/9
        """
        try:
            if '/' in value:
                num, denom = map(int, value.split('/'))
                if num != 1 or denom < 2 or denom > 9:
                    raise ValueError
                return num / denom
            else:
                val = float(value)
                if val < 1 or val > 9:
                    raise ValueError
                return val
        except:
            raise ValueError("Invalid input. Use numbers 1-9 or fractions 1/2-1/9")

    @staticmethod
    def create_reciprocal_matrix(upper_triangle: List[List[float]]) -> np.ndarray:
        """
        Create a complete reciprocal matrix from upper triangle values
        """
        n = len(upper_triangle)
        matrix = np.ones((n, n))
        
        for i in range(n):
            for j in range(i + 1, n):
                matrix[i][j] = upper_triangle[i][j-i-1]
                matrix[j][i] = 1 / matrix[i][j]
        
        return matrix

    @staticmethod
    def calculate_weights(matrix: np.ndarray) -> np.ndarray:
        """
        Calculate priority weights using the geometric mean method
        """
        n = len(matrix)
        # Calculate geometric mean of each row
        geometric_means = np.prod(matrix, axis=1) ** (1/n)
        # Normalize to get weights
        weights = geometric_means / np.sum(geometric_means)
        return weights

    @staticmethod
    def calculate_consistency(matrix: np.ndarray, weights: np.ndarray) -> Tuple[float, float, float]:
        """
        Calculate λmax, CI, and CR for the matrix
        Returns: (lambda_max, CI, CR)
        """
        n = len(matrix)
        
        # Calculate λmax
        weighted_sum = np.dot(matrix, weights)
        lambda_max = np.mean(weighted_sum / weights)
        
        # Calculate CI (Consistency Index)
        ci = (lambda_max - n) / (n - 1) if n > 1 else 0
        
        # Calculate CR (Consistency Ratio)
        ri = AHPCalculator.RI_VALUES.get(n, 1.49)  # Use 1.49 for n > 10
        cr = ci / ri if ri != 0 else 0
        
        return lambda_max, ci, cr

    @staticmethod
    def is_consistent(cr: float, threshold: float = 0.1) -> bool:
        """
        Check if the matrix is consistent based on CR value
        """
        return cr < threshold

    @staticmethod
    def calculate_final_scores(
        criteria_weights: np.ndarray,
        alternative_weights: Dict[str, np.ndarray]
    ) -> Dict[str, float]:
        """
        Calculate final scores for alternatives
        Returns a dictionary of alternative indices and their final scores
        """
        n_alternatives = len(next(iter(alternative_weights.values())))
        final_scores = np.zeros(n_alternatives)
        
        for criterion_idx, criterion_weight in enumerate(criteria_weights):
            criterion_name = f"criterion_{criterion_idx}"
            if criterion_name in alternative_weights:
                final_scores += criterion_weight * alternative_weights[criterion_name]
        
        return {i: score for i, score in enumerate(final_scores)}

    @staticmethod
    def format_matrix_for_display(matrix: np.ndarray) -> List[List[str]]:
        """
        Format matrix values for display
        Converts decimals to fractions where appropriate
        """
        def format_value(val):
            if abs(val - round(val)) < 0.0001:  # For whole numbers
                return str(int(round(val)))
            elif val < 1:  # For fractions less than 1
                return f"1/{int(round(1/val))}"
            else:
                return f"{val:.2f}"

        return [[format_value(val) for val in row] for row in matrix]

    @staticmethod
    def validate_matrix_size(matrix: np.ndarray, min_size: int = 3, max_size: int = 10) -> bool:
        """
        Validate matrix dimensions
        """
        n = len(matrix)
        if n < min_size or n > max_size:
            raise ValueError(f"Matrix must be between {min_size}x{min_size} and {max_size}x{max_size}")
        if not all(len(row) == n for row in matrix):
            raise ValueError("Matrix must be square")
        return True

    @staticmethod
    def process_comparison_matrix(
        input_values: List[List[str]], 
        labels: List[str]
    ) -> Dict[str, Union[np.ndarray, List[str], float]]:
        """
        Process a comparison matrix and return all relevant calculations
        """
        # Convert input values to float matrix
        matrix = np.array([[AHPCalculator.validate_input(val) for val in row] for row in input_values])
        
        # Validate matrix
        AHPCalculator.validate_matrix_size(matrix)
        
        # Calculate weights and consistency measures
        weights = AHPCalculator.calculate_weights(matrix)
        lambda_max, ci, cr = AHPCalculator.calculate_consistency(matrix, weights)
        
        # Format results for display
        formatted_matrix = AHPCalculator.format_matrix_for_display(matrix)
        
        return {
            'matrix': matrix,
            'formatted_matrix': formatted_matrix,
            'weights': weights,
            'labels': labels,
            'lambda_max': lambda_max,
            'ci': ci,
            'cr': cr,
            'is_consistent': AHPCalculator.is_consistent(cr)
        }
