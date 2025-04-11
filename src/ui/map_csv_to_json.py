def map_csv_to_json(df, annotations):
    output_jsons = []
    dimensions_to_each_dim = {}
    for dim, dim_val in annotations[0]["annotations"].items():
        dimensions_to_each_dim[dim] = dim_val["dimensions"]
    for _, row in df.iterrows():
        annotations = {}
        full_prompt = row["prompt"]
        placeholder_prompt = full_prompt
        for col in df.columns:
            if col == "dim_breakdown":
                continue
            if col.startswith("dim_"):
                dim_name = col.replace("dim_", "")
                annotations[dim_name] = {"text": row[col], "dimensions": dimensions_to_each_dim[dim_name]}
                placeholder_prompt = placeholder_prompt.replace(row[col], "{" + dim_name.upper() + "}")
        current_sample_json = {
            "full_prompt": full_prompt,
            "placeholder_prompt": placeholder_prompt,
            "annotations": annotations,
        }
        output_jsons.append(current_sample_json)
    return output_jsons
