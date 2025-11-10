"""
Constants used throughout the backend.
"""

# Rating constants
MIN_RATING = 1
MAX_RATING = 5
HIGH_RATING_THRESHOLD = 4  # Ratings >= this are considered "high rated"

# Generation constants
MIN_VARIATIONS = 1
MAX_VARIATIONS = 6
DEFAULT_VARIATIONS = 4
DEFAULT_IMAGE_SIZE = "1024x1024"  # DALL-E 3 minimum size
VALID_IMAGE_SIZES = ["1024x1024", "1792x1024", "1024x1792"]
DEFAULT_QUALITY = "standard"
VALID_QUALITIES = ["standard", "hd"]

# Analysis constants
MIN_SAMPLES_FOR_ANALYSIS = 3
MIN_DATA_SIZE_FOR_HIGH_CONFIDENCE = 10  # For keyword analysis confidence
MIN_DATA_SIZE_FOR_MEDIUM_CONFIDENCE = 5  # For keyword analysis confidence
HIGH_SUCCESS_RATE_THRESHOLD = 0.7
MEDIUM_SUCCESS_RATE_THRESHOLD = 0.5
LOW_SUCCESS_RATE_THRESHOLD = 0.3

# Performance level thresholds
EXCELLENT_SUCCESS_RATE = 0.7
EXCELLENT_AVG_RATING = 4.0
GOOD_SUCCESS_RATE = 0.5
GOOD_AVG_RATING = 3.5
FAIR_SUCCESS_RATE = 0.3
FAIR_AVG_RATING = 3.0

# Keyword pattern
KEYWORD_PATTERN = r'##(\w+)'

# Stop words for descriptive keyword extraction
STOP_WORDS = {'with', 'and', 'the', 'for', 'are', 'this', 'that'}
MIN_WORD_LENGTH = 3

# Default pagination
DEFAULT_LIMIT = 100
DEFAULT_RECENT_LIMIT = 20

