import pandas as pd
import numpy as np

# Define the Box class
class Box:
    def __init__(self, name, dimensions, weight, quantity=1):
        self.name = name
        self.dimensions = dimensions
        self.weight = weight
        self.quantity = quantity

    def is_similar(self, other_box, tolerance):
        return np.allclose(self.dimensions[1:], other_box.dimensions[1:], atol=tolerance)

    def __repr__(self):
        return f"Box(name={self.name}, dimensions={self.dimensions}, weight={self.weight}, quantity={self.quantity})"

# Define the BoxGrouper class
class BoxGrouper:
    def __init__(self, boxes, tolerance, max_weight):
        self.boxes = boxes
        self.tolerance = tolerance
        self.max_weight = max_weight

    def group_boxes(self):
        groups = []
        for box in self.boxes:
            for _ in range(int(box.quantity)):  # Convert quantity to int for looping
                self._place_in_group(box, groups)
        return groups

    def _place_in_group(self, box, groups):
        best_group = None
        best_weight_diff = float('inf')  # Initialize with a large value

        for group in groups:
            current_weight = sum(b.weight for b in group)
            potential_weight = current_weight + box.weight
            weight_diff = abs(self.max_weight - potential_weight)

            if potential_weight <= self.max_weight and weight_diff < best_weight_diff and box.is_similar(group[0], self.tolerance):
                best_group = group
                best_weight_diff = weight_diff

        if best_group is not None:
            best_group.append(box)
        else:
            groups.append([box])

# Define the GroupGrouper class
class GroupGrouper:
    def __init__(self, groups, max_weight):
        self.groups = groups
        self.max_weight = max_weight

    def group_groups(self):
        final_groups = []
        visited = [False] * len(self.groups)

        for i, group1 in enumerate(self.groups):
            if visited[i]:
                continue
            new_group = [group1]
            visited[i] = True
            current_weight = sum(box.weight for box in group1)

            for j, group2 in enumerate(self.groups):
                if visited[j]:
                    continue

                potential_weight = current_weight + sum(box.weight for box in group2)

                if potential_weight <= self.max_weight:
                    new_group.append(group2)
                    visited[j] = True
                    current_weight += sum(box.weight for box in group2)

            final_groups.append(new_group)

        return final_groups


def process_row(row):
    try:
        # Access columns by index (5, 7, 8)
        mm = float(row.iloc[5])
        boy = float(row.iloc[7])
        en = float(row.iloc[8])

        dimensions = (mm, boy, en)
        # print("Dimensions:", dimensions)

    except ValueError as e:
        print("Error converting data to float:", e)
        dimensions = (0.0, 0.0, 0.0)  # Default values
        print("Default dimensions set:", dimensions)

    return dimensions

def read_and_filter_boxes(file_path, filter_value):
    # Read the Excel file with header in the second row
    df = pd.read_excel(file_path, header=1)

    # Print the columns to understand their names and positions
    #print("Columns in the DataFrame:", df.columns)

    # Print the first few rows to understand the data
    #print("First few rows of the DataFrame:")
    #print(df.head())

    # Filter the DataFrame based on the specified value in the 'R' column (Unnamed: 17)
    filtered_df = df[df['ÜRÜN\nMODÜL ADI'] == filter_value]



    boxes = []
    for index, row in filtered_df.iterrows():
        name = row['PARÇA ADI']  # Adjust this if necessary

        quantity = 0.0

        # Convert quantity to float, skip if not possible
        try:
            quantity = float(row['Unnamed: 9']) if not pd.isna(row['Unnamed: 9']) else 0.0
            # print("quantity",quantity)
        except ValueError:
            quantity = 0.0

        # Get dimensions, convert to float, skip if not possible
        dimensions = (0.0, float(row['BİTMİŞ Y.L EBAT']), float(row['Unnamed: 8']))
        mm = str(row['MM'])
        # print("dimension:: ", mm, ", ", dimensions[1], ",", dimensions[2])

        # Get weight, convert to float, skip if not possible
        try:
            weight = float(row['Ağırlık']) / quantity if not pd.isna(row['Ağırlık']) else 0.0
        except ValueError:
            weight = 0.0

        boxes.append(Box(name=name, dimensions=dimensions, weight=weight, quantity=quantity))

    return boxes

# Define the file path to your Excel file
file_path = 'veriseti.xls'
filter_value = 'KONSOL'  # The value to filter in the 'R' column
# filter_value = '6 LI SÜRGÜLÜ DOLAP'



# Read and filter boxes
filtered_boxes = read_and_filter_boxes(file_path, filter_value)

# Set tolerance and weight limits
tolerance = 200.0
max_weight = 36

# Print the filtered boxes
print("Filtered Boxes:")
for box in filtered_boxes:
    print(box)



# Create a BoxGrouper instance
grouper = BoxGrouper(filtered_boxes, tolerance, max_weight)

# Group the boxes
groups = grouper.group_boxes()

# Print the initial groups
total_w = 0.0
print("\n---------------------------------------------\nInitial Groups:")
for i, group in enumerate(groups, 1):
    group_names = [box.name for box in group]
    group_dims = [box.dimensions for box in group]
    group_weight = sum(box.weight for box in group)
    # print(f"Group {i}:")
    # print(f"  Names = {group_names}")
    # print(f"  Dimensions = {group_dims}")
    # print(f"  Total Weight = {group_weight} kg")

    group_weight = sum(box.weight for box in group)
    total_w += group_weight

print(f"------------------------------------\n  Total Weight = {total_w} kg \n---------------------------------------------")

# Now, let's group the groups
group_grouper = GroupGrouper(groups, max_weight)
final_groups = group_grouper.group_groups()

# Print the final grouped groups
total_final_group = 0.0
print("\n--------------------------------------------\nFinal Grouped Groups:")
total_weight = 0
for i, final_group in enumerate(final_groups, 1):
    all_groups = []
    group_total_weight = 0
    total_final_group += 1
    for group in final_group:
        group_names = [box.name for box in group]
        group_dims = [box.dimensions for box in group]
        group_weight = sum(box.weight for box in group)
        all_groups.append((group_names, group_dims, group_weight))
        group_total_weight += group_weight

    total_weight += group_total_weight
    print(f"Final Group {i}:")
    for names, dims, weight in all_groups:
        print(f"  Group with Names = {names}")
        print(f"  Dimensions = {dims}")
        print(f"  Group Weight = {weight} kg")

    print(f" \n Total Weight of Final Group {i} = {group_total_weight} kg\n---------------------------------------------")

print(f"------------------------------------\n   Total Final Groups: {total_final_group} \n---------------------------------------------")
print(f"------------------------------------\n  Total Weight = {total_w} kg \n---------------------------------------------")

weight_per_pack = (total_w/total_final_group) - ((0.05*total_w)/100)
print(f"------------------------------------\n  Weight per pack: {weight_per_pack}   \n---------------------------------------------")





# # Print the initial groups
# print("Initial Groups:")
# for i, group in enumerate(groups, 1):
#     group_names = [box.name for box in group]
#     group_dims = [box.dimensions for box in group]
#     group_weight = sum(box.weight for box in group)
#     print(f"Group {i}: Names = {group_names}, Dimensions = {group_dims}, Total Weight = {group_weight} kg")
#
# # Now, let's group the groups
# group_grouper = GroupGrouper(groups, max_weight)
# final_groups = group_grouper.group_groups()
#
# # Print the final grouped groups
# print("\nFinal Grouped Groups:")
# for i, final_group in enumerate(final_groups, 1):
#     all_groups = []
#     total_weight = 0
#     for group in final_group:
#         group_names = [box.name for box in group]
#         group_dims = [box.dimensions for box in group]
#         group_weight = sum(box.weight for box in group)
#         all_groups.append((group_names, group_dims, group_weight))
#         total_weight += group_weight
#     print(f"Final Group {i}:")
#     for names, dims, weight in all_groups:
#         print(f"    Group with Names = {names}, Dimensions = {dims}, Group Weight = {weight} kg")
#     print(f"    Total Weight of Final Group {i} = {total_weight} kg")
