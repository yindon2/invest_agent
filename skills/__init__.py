"""
投资学AI Agent - Skills模块
"""

from .fundamental import FundamentalAnalysisSkill
from .macro_analysis import MacroAnalysisSkill
from .visualization import VisualizationSkill
from .cross_validate import CrossValidationSkill, AnomalyDetector

__all__ = [
    'FundamentalAnalysisSkill',
    'MacroAnalysisSkill',
    'VisualizationSkill',
    'CrossValidationSkill',
    'AnomalyDetector'
]
