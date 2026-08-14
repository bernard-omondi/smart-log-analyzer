"""
Visualization module for smart-log-analyzer.
Generates charts from the database.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from src.db import get_connection

# Set style for professional-looking charts
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

def fetch_hourly_data():
    """Fetch hourly volume data from database."""
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT 
            timestamp_utc,
            strftime('%Y-%m-%d %H:00:00', timestamp_utc) as hour,
            COUNT(*) as request_count
        FROM logs
        GROUP BY hour
        ORDER BY hour ASC
    """, conn)
    conn.close()
    df['hour'] = pd.to_datetime(df['hour'])
    return df

def fetch_status_data():
    """Fetch status code distribution from database."""
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT 
            status,
            COUNT(*) as count
        FROM logs
        GROUP BY status
        ORDER BY status ASC
    """, conn)
    conn.close()
    return df

def fetch_top_ips(limit=10):
    """Fetch top IPs from database."""
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT 
            ip,
            COUNT(*) as request_count
        FROM logs
        GROUP BY ip
        ORDER BY request_count DESC
        LIMIT ?
    """, conn, params=(limit,))
    conn.close()
    return df

def plot_hourly_volume(save_path='hourly_volume.png'):
    """Plot hourly request volume."""
    df = fetch_hourly_data()
    
    plt.figure(figsize=(14, 6))
    plt.plot(df['hour'], df['request_count'], marker='o', linestyle='-', linewidth=2, markersize=4)
    plt.title('Hourly Request Volume', fontsize=16, fontweight='bold')
    plt.xlabel('Hour', fontsize=12)
    plt.ylabel('Number of Requests', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"✅ Saved hourly volume chart to {save_path}")
    plt.show()
    
    return df

def plot_status_distribution(save_path='status_distribution.png'):
    """Plot status code distribution as a bar chart."""
    df = fetch_status_data()
    
    # Color code by status type
    colors = []
    for status in df['status']:
        if status < 300:
            colors.append('green')
        elif status < 400:
            colors.append('blue')
        elif status < 500:
            colors.append('orange')
        else:
            colors.append('red')
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(df['status'].astype(str), df['count'], color=colors)
    plt.title('HTTP Status Code Distribution', fontsize=16, fontweight='bold')
    plt.xlabel('Status Code', fontsize=12)
    plt.ylabel('Count', fontsize=12)
    
    # Add value labels on bars
    for bar, count in zip(bars, df['count']):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                 f'{count}', ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"✅ Saved status distribution chart to {save_path}")
    plt.show()
    
    return df

def plot_top_ips(limit=10, save_path='top_ips.png'):
    """Plot top IPs by request count."""
    df = fetch_top_ips(limit)
    
    plt.figure(figsize=(12, 6))
    bars = plt.barh(df['ip'], df['request_count'], color='steelblue')
    plt.title(f'Top {limit} IPs by Request Count', fontsize=16, fontweight='bold')
    plt.xlabel('Number of Requests', fontsize=12)
    plt.ylabel('IP Address', fontsize=12)
    
    # Add value labels
    for bar, count in zip(bars, df['request_count']):
        plt.text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2,
                 f'{count}', va='center', fontsize=10)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"✅ Saved top IPs chart to {save_path}")
    plt.show()
    
    return df

def generate_all_charts():
    """Generate all visualizations."""
    print("📊 Generating visualizations...")
    
    # Create visualizations directory if it doesn't exist
    import os
    os.makedirs('visualizations', exist_ok=True)
    
    try:
        hourly_df = plot_hourly_volume(save_path='visualizations/hourly_volume.png')
        print(f"   📈 Hourly volume: {len(hourly_df)} data points")
        
        status_df = plot_status_distribution(save_path='visualizations/status_distribution.png')
        print(f"   📊 Status codes: {len(status_df)} unique codes")
        
        top_ips_df = plot_top_ips(limit=10, save_path='visualizations/top_ips.png')
        print(f"   🌐 Top IPs: {len(top_ips_df)} IPs shown")
        
        print("✅ All visualizations generated successfully!")
        print(f"📁 Charts saved to: visualizations/")
        
    except Exception as e:
        print(f"❌ Error generating visualizations: {e}")
        print("   Make sure you have data in the database (run ingest first)")
if __name__ == '__main__':
    generate_all_charts()
