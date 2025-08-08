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

def main():
    base_dir = os.path.dirname(__file__)
    expected_path = os.path.join(base_dir, "jsons", "position.json")
    student_css_path = os.path.join(os.path.dirname(base_dir), "labDirectory", "position", "style.css")

    with open(expected_path, 'r') as f:
        expected = json.load(f)

    student_styles = parse_css(student_css_path)

    results = []
    for selector, props in expected.items():
        for prop, expected_val in props.items():
            student_val = student_styles.get(selector, {}).get(prop)
            if student_val and student_val == expected_val.lower():
                results.append({
                    "testid": f"{selector}/{prop}",
                    "status": "success",
                    "score": 1,
                    "maximum marks": 1,
                    "message": f"{selector} has correct {prop} value"
                })
            else:
                results.append({
                    "testid": f"{selector}/{prop}",
                    "status": "failure",
                    "score": 0,
                    "maximum marks": 1,
                    "message": f"Expected '{expected_val}' for {prop} in {selector}, but got '{student_val}'"
                })

    output_path = os.path.join(base_dir, "evaluate.json")
    with open(output_path, 'w') as f:
        json.dump({"data": results}, f, indent=4)

if __name__ == "__main__":
    main()

