import json
import os
import tinycss2

def parse_css(file_path):
    with open(file_path, 'r') as f:
        css_content = f.read()
    rules = tinycss2.parse_stylesheet(css_content, skip_comments=True, skip_whitespace=True)
    styles = {}
    for rule in rules:
        if rule.type == 'qualified-rule':
            selector = ''.join(
                [t.serialize().strip() for t in rule.prelude if t.type != 'whitespace']
            ).strip()
            declarations = tinycss2.parse_declaration_list(rule.content)
            props = {}
            for decl in declarations:
                if decl.type == 'declaration':
                    prop_name = decl.name.strip().lower()
                    prop_value = ''.join([t.serialize().strip() for t in decl.value]).strip().lower()
                    props[prop_name] = prop_value
            styles[selector] = props
    return styles

def extract_zindex(styles, selector):
    val = styles.get(selector, {}).get("z-index")
    if val is None:
        return None
    try:
        return int(val)
    except ValueError:
        return None

def main():
    base_dir = os.path.dirname(__file__)

    student_css_path = os.path.join(os.path.dirname(base_dir), "labDirectory", "zindex", "style.css")
    student_styles = parse_css(student_css_path)

    order = [".box1", ".box2", ".box3", ".text-overlay"]

    z_values = {sel: extract_zindex(student_styles, sel) for sel in order}

    results = []
    missing = [sel for sel, val in z_values.items() if val is None]

    if missing:
        for sel in missing:
            results.append({
                "testid": f"{sel}/z-index",
                "status": "failure",
                "score": 0,
                "maximum marks": 1,
                "message": f"No valid z-index found for {sel}"
            })
    else:
        z_values = {k: int(v) for k, v in z_values.items()}
        correct_order = all(z_values[order[i]] < z_values[order[i+1]] for i in range(len(order)-1))

        if correct_order:
            results.append({
                "testid": "zindex/relative-order",
                "status": "success",
                "score": 4,
                "maximum marks": 4,
                "message": "z-index values are in correct relative order"
            })
        else:
            results.append({
                "testid": "zindex/relative-order",
                "status": "failure",
                "score": 0,
                "maximum marks": 4,
                "message": f"z-index values not in correct relative order: {z_values}"
            })

    output_path = os.path.join(base_dir, "evaluate.json")
    with open(output_path, 'w') as f:
        json.dump({"data": results}, f, indent=4)

if __name__ == "__main__":
    main()

