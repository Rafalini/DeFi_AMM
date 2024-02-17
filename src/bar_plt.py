import matplotlib.pyplot as plt

# Sample data for the bar charts
categories = ['Górnicy', 'Atakujący']
values1 = [78, 22]
values2 = [93, 7]
values3 = [98, 2]

# Create subplots with 1 row and 3 columns
fig, axs = plt.subplots(1, 3, figsize=(12, 4))  # Adjust figsize as needed
plt.suptitle('Udział procentowy w ilości generowanych bloków przez atakującego', fontsize=25)
axis_number_font_size = 15
axs[0].tick_params(axis='both', which='major', labelsize=axis_number_font_size)
axs[0].tick_params(axis='both', which='minor', labelsize=axis_number_font_size)
axs[1].tick_params(axis='both', which='major', labelsize=axis_number_font_size)
axs[1].tick_params(axis='both', which='minor', labelsize=axis_number_font_size)
axs[2].tick_params(axis='both', which='major', labelsize=axis_number_font_size)
axs[2].tick_params(axis='both', which='minor', labelsize=axis_number_font_size)

axs[0].set_ylim(0,100)
axs[1].set_ylim(0,100)
axs[2].set_ylim(0,100)
# Plot the first bar chart
axs[0].bar(categories[0], values1[0], color='skyblue')
axs[0].bar(categories[1], values1[1], color='salmon')
axs[0].set_title('Dwóch górników łącznie', fontsize=25)

# Plot the second bar chart
axs[1].bar(categories[0], values2[0], color='skyblue')
axs[1].bar(categories[1], values2[1], color='salmon')
axs[1].set_title('Czterech górników łącznie', fontsize=25)

# Plot the third bar chart
axs[2].bar(categories[0], values3[0], color='skyblue')
axs[2].bar(categories[1], values3[1], color='salmon')
axs[2].set_title('Sześciu górników łącznie', fontsize=25)

# Adjust layout
plt.tight_layout()

# Show the plot
plt.show()
