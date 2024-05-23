import bpy
import json
import os
import math

def define_materials(update=False):
    materials = {
        "1": {
            "name": "Structural Steel",
            "elasticity_modulus": 29000,  # ksi
            "density": 490,              # lb/ft^3
            "ultimate_strength": 58,     # ksi
            "yield_strength": 36,        # ksi
            "thermal_expansion_coefficient": 6.5,  # per degree Fahrenheit
            "poissons_ratio": 0.3
        },
        "2": {
            "name": "Concrete",
            "elasticity_modulus": 4000,  # ksi
            "density": 150,              # lb/ft^3
            "ultimate_strength": 5,      # ksi
            "yield_strength": 3,         # ksi
            "thermal_expansion_coefficient": 5.5,  # per degree Fahrenheit
            "poissons_ratio": 0.2
        },
        "3": {
            "name": "Wood",
            "elasticity_modulus": 1,  # ksi
            "density": 16,               # lb/ft^3
            "ultimate_strength": 4,      # ksi
            "yield_strength": 2,         # ksi
            "thermal_expansion_coefficient": 1,   # per degree Fahrenheit
            "poissons_ratio": 0.33
        }
    }
    
    if update:
        # Logic to update materials based on external inputs or changes
        pass

    return materials


def add_loads_to_plates(plates, mesh):
    """
    Create a dictionary of loads for each plate based on orientation and direction determined by normals.

    Args:
    plates (dict): Dictionary containing the plates with their node indices.
    mesh (bpy.types.Mesh): Blender Mesh data from which normals can be extracted.

    Returns:
    dict: Dictionary of loads corresponding to each plate.
    """
    area_loads = {}
    for plate_id, plate_info in plates.items():
        nodes_indices = plate_info['nodes'].split(',')
        # Calculate average normal for the plate based on its nodes
        # Retrieve vertex positions for the triangular plate
        vertices = [mesh.vertices[int(idx) - 1].co for idx in nodes_indices]

        # Calculate the normal using the new robust function
        
        try:
            normal = calculate_normal(vertices[:3])
        except:
            normal = False
        # Determine if the plate is primarily horizontal or vertical
        if normal == False:
            load_magnitude = 100
            load_direction = 'Z'
        elif abs(normal[2]) > 0.5:  # Threshold for 'upwards' normal, tweak as needed
            load_magnitude = .15  # Typical for horizontal surfaces like roofs
            load_direction = 'Y'
        else:
            load_magnitude = 0.08  # Typical for vertical surfaces like walls
            load_direction = determine_load_direction(normal)

        area_loads[plate_id] = {
            "type": "one_way",
            "nodes": plate_info['nodes'],
            "members": 0,
            "mag": load_magnitude,
            "direction": load_direction,
            "elevations": 0,
            "mags": 0,
            "column_direction": ','.join(nodes_indices[:2]),  # Using first two nodes as column direction
            "elevation_direction": "",
            "loaded_members_axis": "all",
            "LG": "LG"
        }
    return area_loads

def determine_load_direction(normal):
    """
    Determines the primary load direction based on the average normal vector of a vertical plate.

    Args:
    normal (list): The average normal vector [x, y, z] of the plate.

    Returns:
    str: Primary direction for the load based on the plate's facing, accounting for global coordinates.
    """
    # Normalize the normal vector for reliable angle calculations
    norm_length = math.sqrt(normal[0]**2 + normal[1]**2 + normal[2]**2)
    normalized_normal = [normal[i] / norm_length for i in range(3)]

    # Calculate angle in the XY-plane
    angle = math.atan2(normalized_normal[1], normalized_normal[0]) * (180 / math.pi)  # Convert angle to degrees

    # Determine direction based on the angle
    if -45 <= angle < 45:
        return 'X'  # Assuming positive X-axis faces East, load applied along Z-axis
    elif 45 <= angle < 135:
        return 'Z'  # Assuming positive Y-axis faces North, load applied along X-axis
    elif -135 <= angle < -45:
        return 'Z'  # Assuming negative Y-axis faces South, load applied along X-axis
    else:
        return 'X'  # Assuming negative X-axis faces West, load applied along Z-axis

def calculate_normal(vertices):
    """
    Calculate the normal of a triangular plate from its vertices.

    Args:
    vertices (list of tuples): List of 3D coordinates for the vertices of the triangle.

    Returns:
    list: Normal vector of the triangular plate.
    """
    # Extract the three vertices
    v1, v2, v3 = vertices

    # Vector from v1 to v2
    vector1 = [v2[i] - v1[i] for i in range(3)]
    # Vector from v1 to v3
    vector2 = [v3[i] - v1[i] for i in range(3)]

    # Cross product of vector1 and vector2 gives the normal vector
    normal = [
        vector1[1] * vector2[2] - vector1[2] * vector2[1],  # X
        vector1[2] * vector2[0] - vector1[0] * vector2[2],  # Y
        vector1[0] * vector2[1] - vector1[1] * vector2[0]   # Z
    ]

    # Normalize the normal vector
    norm_length = math.sqrt(sum(n**2 for n in normal))
    normalized_normal = [n / norm_length for n in normal]

    return normalized_normal


def create_plates_from_mesh_data(mesh):
    plates_specs = []
    for poly in mesh.polygons:
        nodes = [str(i + 1) for i in poly.vertices]
        plates_specs.append({
            "nodes": ",".join(nodes),
            "thickness": 0.39370078740157477,  # example thickness
            "material_id": 3,  # example material ID
        })
    return create_plates(plates_specs)

def create_plates(plate_specs):
    """
    Create a dictionary of plates based on the provided specifications.
    """
    plates = {}
    for i, spec in enumerate(plate_specs):
        plate_id = str(i + 1)
        plates[plate_id] = {
            "nodes": spec.get("nodes", ""),
            "thickness": spec.get("thickness", 0.39370078740157477),
            "material_id": spec.get("material_id", 3),
            "rotZ": spec.get("rotZ", 0),
            "type": spec.get("type", "auto"),
            "diaphragm": spec.get("diaphragm", "no"),
            "offset": spec.get("offset", 0),
            "state": spec.get("state", "stress"),
            "drilling_stiffness_factor": spec.get("drilling_stiffness_factor", 1),
            "holes": spec.get("holes", []),
            "diaphragm_internal_nodes": spec.get("diaphragm_internal_nodes"),
            "diaphragm_fixity": spec.get("diaphragm_fixity", "auto"),
            "membrane_thickness": spec.get("membrane_thickness", ""),
            "bending_thickness": spec.get("bending_thickness", ""),
            "shear_thickness": spec.get("shear_thickness", ""),
            "isMeshed": spec.get("isMeshed", False)
        }
    return plates

def extract_mesh_data():
    nodes = {}
    members = {}
    supports = {}
    
    # Loop through all mesh objects in the scene to extract data
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            mesh = obj.data
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='OBJECT')

            # Map vertices to node IDs
            vertex_map = {}
            for i, vertex in enumerate(mesh.vertices):
                node_id = len(nodes) + 1
                vertex_map[vertex.index] = node_id
                nodes[node_id] = {
                    "x": vertex.co.x,
                    "y": vertex.co.z,  # Adjust axis based on project specifics
                    "z": vertex.co.y
                }
                
                # Define supports at nodes where vertex.co.z is 0 (assumed ground level)
                if vertex.co.z == 0:
                    supports[node_id] = {
                        "type": "node",
                        "direction_code": "BBBBBB",
                        "tx": 0, "ty": 0, "tz": 0,
                        "rx": 0, "ry": 0, "rz": 0,
                        "node": node_id,
                        "restraint_code": "FFFFFF"
                    }
                
            # Define members based on edges in the mesh
            for edge in mesh.edges:
                member_id = len(members) + 1
                members[member_id] = {
                    "type": "normal_continuous",
                    "cable_length": None,
                    "node_A": vertex_map[edge.vertices[0]],
                    "node_B": vertex_map[edge.vertices[1]],
                    "section_id": 1,
                    "rotation_angle": 0,
                    "fixity_A": "FFFFFF",
                    "fixity_B": "FFFFFF",
                    "offset_Ax": "0", "offset_Ay": "0", "offset_Az": "0",
                    "offset_Bx": "0", "offset_By": "0", "offset_Bz": "0",
                    "stiffness_A_Ry": 0, "stiffness_A_Rz": 0,
                    "stiffness_B_Ry": 0, "stiffness_B_Rz": 0,
                    "mirror": "no",
                    "disable_non_linear_effects": "no"
                }
                
    return nodes, members, supports

# Extracting data from the scene
nodes, members, supports = extract_mesh_data()

# Assuming 'bpy.context.object.data' is the mesh data
mesh_data = bpy.context.object.data

plates = create_plates_from_mesh_data(mesh_data)


# Add loads to plates
area_loads = add_loads_to_plates(plates, mesh_data)


materials = define_materials()

# Create output structure
output_data = {"dataVersion": 42,
                "settings": 
                    {"units":
                {"length":"ft",
                    "section_length":"in",
                "material_strength":"ksi",
                "density":"lb/ft3",
                "force":"kip",
                "moment":"kip-ft",
                "pressure":"ksf",
                "mass":"kip",
                "temperature":"degf",
                "translation":"in",
            "stress":"ksi"},
                "precision":"fixed",
                "precision_values":3,
                "evaluation_points":5,
                "apply_evaluation_points_to_continuous_member_spans":False,
                "continuous_member_node_detection_tolerance":"0",
                "vertical_axis":"Y",
                "member_offsets_axis":"local",
                "projection_system":"orthographic",
                "solver_timeout":90,
                "linear_equation_solver":"direct_1",
                "smooth_plate_nodal_results":True,
                "extrapolate_plate_results_from_gauss_points":False,
                "calculate_shear_properties_of_wood_concrete_sections":True,
                "buckling_johnson":False,
                "non_linear_tolerance":"1",
                "non_linear_theory":"small",
                "auto_stabilize_model":False,
                "only_solve_user_defined_load_combinations":False,
                "include_rigid_links_for_area_loads":False,
                "dynamic_modes":"5",
                "dynamic_frequency_area_reduction_factor":"1",
                "envelope_alternate_method":True,
                "thumbnail":
            {"visibility":
                {"nodes":True,
                    "node_labels":True,
                "member_labels":True,
                "supports":True,
                "loads":True,
            "load_labels":True}
            },
                "analysis_types":
            {"linear_static":True,
                "linear_buckling":False,
            "non_linear_static":False,
            "dynamic_frequency":False,
            "response_spectrum":False},
            "visibility":
            {"nodes":True,
                "node_labels":True,
            "members":True,
            "member_labels":True,
            "member_end_fixities":True,
            "rigid_links":True,
            "plates":True,
            "plate_labels":True,
            "mesh":True,
            "mesh_nodes":True,
            "supports":True,
            "loads":True,
            "load_labels":True,
            "local_axis":False,
            "graphics_font_size":"3"}},
            "details":
            {},
    "nodes": nodes,
    "members": members,
    "supports": supports,
    "materials": materials,
    "plates": plates,
    "sections":{
    "1":{
"name":"","material_id":1,"area":0.379,"Iy":2.08,"Iz":.209,"J":0.000151}},
}
# Include these loads in the output structure
output_data['area_loads'] = area_loads

# Define path for output
save_path = 'C:\\Users\\jb\\Documents\\structure_data_completex.json'

# Save the data to a JSON file
with open(save_path, 'w') as f:
    json.dump(output_data, f, indent=4)

print(f"JSON data has been saved to {save_path}")
