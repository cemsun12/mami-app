import pandas as pd
import numpy as np

class Box:
    def __init__(self, name, dimensions, weight, quantity=1.0):
        self.name = name
        self.dimensions = dimensions
        self.weight = weight
        self.quantity = quantity

    def is_similar(self, other_box, tolerance):
        return np.allclose(self.dimensions[1:], other_box.dimensions[1:], atol=tolerance)

    def __repr__(self):
        return f"Box(name={self.name}, dimensions={self.dimensions}, weight={self.weight}, quantity={self.quantity})"


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


def read_boxes_from_excel(file_path):
    df = pd.read_excel(file_path)

    boxes = []
    for index, row in df.iterrows():
        name = row['Parça Adı']
        quantity = row['Adet'] if not pd.isna(row['Adet']) else 0.0
        dimensions = (row['Kalınlık'], row['Boy'], row['En'])
        weight = row['Ağırlık']

        if isinstance(quantity, float):
            quantity = quantity
        else:
            quantity = float(quantity)

        boxes.append(Box(name=name, dimensions=dimensions, weight=weight, quantity=quantity))

    return boxes


# Define the file path to your Excel file
file_path = 'veriseti-demo.xlsx'

# Load the boxes from the Excel file
boxes = read_boxes_from_excel(file_path)

# Set tolerance and weight limits
tolerance = 5.0
max_weight = 49.0

# Create a BoxGrouper instance
grouper = BoxGrouper(boxes, tolerance, max_weight)

# Group the boxes
groups = grouper.group_boxes()

# Print the initial groups
print("Initial Groups:")
for i, group in enumerate(groups, 1):
    group_names = [box.name for box in group]
    group_dims = [box.dimensions for box in group]
    group_weight = sum(box.weight for box in group)
    print(f"Group {i}: Names = {group_names}, Dimensions = {group_dims}, Total Weight = {group_weight} kg")

# Now, let's group the groups
group_grouper = GroupGrouper(groups, max_weight)
final_groups = group_grouper.group_groups()

# Print the final grouped groups
print("\nFinal Grouped Groups:")
for i, final_group in enumerate(final_groups, 1):
    all_groups = []
    total_weight = 0
    for group in final_group:
        group_names = [box.name for box in group]
        group_dims = [box.dimensions for box in group]
        group_weight = sum(box.weight for box in group)
        all_groups.append((group_names, group_dims, group_weight))
        total_weight += group_weight
    print(f"Final Group {i}:")
    for names, dims, weight in all_groups:
        print(f"    Group with Names = {names}, Dimensions = {dims}, Group Weight = {weight} kg")
    print(f"    Total Weight of Final Group {i} = {total_weight} kg")
