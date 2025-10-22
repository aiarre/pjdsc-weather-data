# Flood Prediction Analysis
# Data Science Project: Predicting Road Flooding Based on Weather Conditions
# 
# This notebook analyzes flood data and weather conditions to build a predictive model
# for identifying which roads are likely to be flooded given weather conditions.

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Set up plotting style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

# Set random seed for reproducibility
np.random.seed(42)

print("Libraries imported successfully!")
print(f"Pandas version: {pd.__version__}")
print(f"NumPy version: {np.__version__}")
