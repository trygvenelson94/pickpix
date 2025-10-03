#!/usr/bin/env python3
"""
Extract bar heights from a bar chart image using pixel measurements.
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt

def extract_bar_chart_data(image_path):
    """
    Extract bar heights from a bar chart image.
    Assumes bars are vertical and relatively uniform in width.
    """
    # Read the image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not read image at {image_path}")
        return None
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Display image for user to select reference points
    print("\n" + "="*70)
    print("INSTRUCTIONS:")
    print("="*70)
    print("1. The image will be displayed")
    print("2. Click on two points to define the y-axis scale:")
    print("   - First click: Top of y-axis (max value, e.g., 1.4 M)")
    print("   - Second click: Bottom of y-axis (min value, e.g., 0 M)")
    print("3. Close the image window when done")
    print("="*70)
    
    # Show image and get user clicks
    fig, ax = plt.subplots(figsize=(15, 6))
    ax.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    ax.set_title("Click: (1) Top of Y-axis, (2) Bottom of Y-axis")
    
    clicks = []
    def onclick(event):
        if event.xdata is not None and event.ydata is not None:
            clicks.append((int(event.xdata), int(event.ydata)))
            print(f"  Click {len(clicks)}: x={int(event.xdata)}, y={int(event.ydata)}")
            # Draw horizontal line instead of circle (diameter = 10, so half-width = 5)
            line_half_width = 5
            ax.plot([event.xdata - line_half_width, event.xdata + line_half_width], 
                   [event.ydata, event.ydata], 'r-', linewidth=2)
            fig.canvas.draw()
            if len(clicks) >= 2:
                print("\n✓ Got both reference points. Close the window to continue.")
    
    fig.canvas.mpl_connect('button_press_event', onclick)
    plt.show()
    
    if len(clicks) < 2:
        print("Error: Need 2 reference points")
        return None
    
    # Get y-axis scale
    y_top = clicks[0][1]
    y_bottom = clicks[1][1]
    
    print("\nEnter the actual values for these reference points:")
    y_top_value = float(input(f"  Value at top (y={y_top}): "))
    y_bottom_value = float(input(f"  Value at bottom (y={y_bottom}): "))
    
    # Calculate scale
    pixels_per_unit = (y_bottom - y_top) / (y_top_value - y_bottom_value)
    
    print(f"\n✓ Scale: {pixels_per_unit:.2f} pixels per unit")
    
    # Now measure bars
    print("\n" + "="*70)
    print("BAR MEASUREMENT MODE")
    print("="*70)
    print("For each bar, click at the TOP of the bar")
    print("Close window when done with all bars")
    print("="*70)
    
    # Show image again for bar measurements
    fig2, ax2 = plt.subplots(figsize=(15, 6))
    ax2.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    ax2.axhline(y=y_bottom, color='r', linestyle='--', label='Zero line')
    ax2.set_title("Click at the TOP of each bar (left to right)")
    ax2.legend()
    
    bar_tops = []
    def onclick_bars(event):
        if event.xdata is not None and event.ydata is not None:
            bar_tops.append((int(event.xdata), int(event.ydata)))
            
            # Calculate value
            pixel_height = y_bottom - int(event.ydata)
            value = y_bottom_value + (pixel_height / pixels_per_unit)
            
            print(f"  Bar {len(bar_tops)}: x={int(event.xdata)}, y={int(event.ydata)} → Value={value:.3f}")
            
            # Draw horizontal line instead of circle (diameter = 8, so half-width = 4)
            line_half_width = 4
            ax2.plot([event.xdata - line_half_width, event.xdata + line_half_width], 
                    [event.ydata, event.ydata], 'g-', linewidth=2)
            ax2.text(event.xdata, event.ydata-20, f'{value:.2f}', 
                    fontsize=8, ha='center', color='green', fontweight='bold')
            fig2.canvas.draw()
    
    fig2.canvas.mpl_connect('button_press_event', onclick_bars)
    plt.show()
    
    # Calculate all values
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    
    results = []
    for i, (x, y) in enumerate(bar_tops):
        pixel_height = y_bottom - y
        value = y_bottom_value + (pixel_height / pixels_per_unit)
        results.append(value)
        print(f"Bar {i+1}: {value:.3f}")
    
    return results


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python extract_bar_heights.py <image_path>")
        print("\nExample:")
        print("  python extract_bar_heights.py elution_chart.png")
        sys.exit(1)
    
    image_path = sys.argv[1]
    print(f"Processing: {image_path}")
    
    results = extract_bar_chart_data(image_path)
    
    if results:
        print("\n" + "="*70)
        print("Copy these values:")
        print("="*70)
        # Group by 3
        for i in range(0, len(results), 3):
            group = results[i:i+3]
            print("\t".join([f"{v:.2f}" for v in group]))
