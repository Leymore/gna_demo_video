import os
import re
import json
from jinja2 import Template
import shutil
settings = [
    dict(
        name="na_k18x24x24",
        root_group=[
            ("/data/data0/fzhou87/repos/gna/HunyuanVideo/results/demo/na_k18x24x24_s1x1x1", "NA_s1x1x1"),
            ("/data/data0/fzhou87/repos/gna/HunyuanVideo/results/demo/na_k18x24x24_s2x2x2", "NA_s2x2x2"),
            ("/data/data0/fzhou87/repos/gna/HunyuanVideo/results/demo/na_k18x24x24_s3x4x4", "NA_s3x4x4"),
            ("/data/data0/fzhou87/repos/gna/HunyuanVideo/results/demo/na_k18x24x24_s6x8x8", "NA_s6x8x8"),
            ("/data/data0/fzhou87/repos/gna/HunyuanVideo/results/demo/na_k18x24x24_s9x12x12", "NA_s9x12x12"),
            ("/data/data0/fzhou87/repos/gna/HunyuanVideo/results/demo/sa", "FA"),
        ],
    ),
    dict(
        name="na_k24x32x32",
        root_group=[
            ("/data/data0/fzhou87/repos/gna/HunyuanVideo/results/demo/na_k24x32x32_s1x1x1", "NA_s1x1x1"),
            ("/data/data0/fzhou87/repos/gna/HunyuanVideo/results/demo/na_k24x32x32_s2x2x2", "NA_s2x2x2"),
            ("/data/data0/fzhou87/repos/gna/HunyuanVideo/results/demo/na_k24x32x32_s3x4x4", "NA_s3x4x4"),
            ("/data/data0/fzhou87/repos/gna/HunyuanVideo/results/demo/na_k24x32x32_s6x8x8", "NA_s6x8x8"),
            ("/data/data0/fzhou87/repos/gna/HunyuanVideo/results/demo/na_k24x32x32_s12x16x16", "NA_s12x16x16"),
            ("/data/data0/fzhou87/repos/gna/HunyuanVideo/results/demo/sa", "FA"),
        ],
    ),
    dict(
        name="na_k30x40x40",
        root_group=[
            ("/data/data0/fzhou87/repos/gna/HunyuanVideo/results/demo/na_k30x40x40_s1x1x1", "NA_s1x1x1"),
            ("/data/data0/fzhou87/repos/gna/HunyuanVideo/results/demo/na_k30x40x40_s2x2x2", "NA_s2x2x2"),
            ("/data/data0/fzhou87/repos/gna/HunyuanVideo/results/demo/na_k30x40x40_s3x4x4", "NA_s3x4x4"),
            ("/data/data0/fzhou87/repos/gna/HunyuanVideo/results/demo/na_k30x40x40_s6x8x8", "NA_s6x8x8"),
            ("/data/data0/fzhou87/repos/gna/HunyuanVideo/results/demo/na_k30x40x40_s10x20x20", "NA_s10x20x20"),
            ("/data/data0/fzhou87/repos/gna/HunyuanVideo/results/demo/sa", "FA"),
        ],
    ),
    dict(
        name="na_k24x32x32_additional",
        root_group=[
            ("/data/data0/fzhou87/repos/gna/HunyuanVideo/results/demo/na_k24x32x32_s1x16x16", "NA_s1x16x16"),
            ("/data/data0/fzhou87/repos/gna/HunyuanVideo/results/demo/na_k24x32x32_s2x8x8", "NA_s2x8x8"),
            ("/data/data0/fzhou87/repos/gna/HunyuanVideo/results/demo/na_k24x32x32_s4x8x8", "NA_s4x8x8"),
            ("/data/data0/fzhou87/repos/gna/HunyuanVideo/results/demo/na_k24x32x32_s8x8x8", "NA_s8x8x8"),
            ("/data/data0/fzhou87/repos/gna/HunyuanVideo/results/demo/na_k24x32x32_s16x4x4", "NA_s6x4x4"),
            ("/data/data0/fzhou87/repos/gna/HunyuanVideo/results/demo/sa", "FA"),
        ],
    ),
]

def get_video_groups(root_group):
    roots = [r[0] for r in root_group]

    root2json_paths = {}
    for root in roots:
        for path in os.listdir(root):
            if path.endswith(".json"):
                root2json_paths.setdefault(root, []).append(os.path.join(root, path))

    # find overlap
    video_groups = []
    for json_path in root2json_paths[roots[0]]:
        json_data = json.load(open(json_path))
        prompt = json_data["prompt"]
        video_paths = [json_path.replace(".json", ".mp4")]
        for root in roots[1:]:
            found = False
            for json_path2 in root2json_paths[root]:
                json_data2 = json.load(open(json_path2))
                prompt2 = json_data2["prompt"]
                if prompt == prompt2:
                    found = True
                    video_paths.append(json_path2.replace(".json", ".mp4"))
                    break
            if not found:
                break
        if len(video_paths) == len(roots):
            video_groups.append(
                {
                    "prompt": prompt.strip('\"'),
                    "video_paths": video_paths
                }
            )
    return video_groups

def make_demo_path(video_path):
    video_basename = os.path.basename(video_path)
    video_basename = video_basename[:-4]  # remove .mp4
    video_basename = video_basename.replace(" ", "_").replace(",", "_").replace(":", "_").replace("(", "_").replace(")", "_").replace(".", "_").replace("'", "_").replace('"', "_")
    video_basename = video_basename + ".mp4"
    demo_path = os.path.join('static', 'videos', video_basename)
    return demo_path

def prepare_render_dict(args, video_groups, demo_root):
    video_titles = [r[1] for r in args["root_group"]]
    prompts, video_urls = [], []
    os.makedirs(demo_root, exist_ok=True)
    os.makedirs(os.path.join(demo_root, "static", "videos"), exist_ok=True)
    for video_group in video_groups:
        prompts.append(video_group['prompt'])
        videos = []
        for video_path in video_group['video_paths']:
            demo_path = make_demo_path(video_path)
            if not os.path.exists(os.path.join(demo_root, demo_path)):
                shutil.copy(video_path, os.path.join(demo_root, demo_path))
            videos.append(demo_path)
        video_urls.append(videos)
    html_subtitle = args["name"].replace("_", " ").upper()
    return dict(video_titles=video_titles, prompts=prompts, video_urls=video_urls, html_subtitle=html_subtitle)


def render_html(pack, output_html_path):
    # import ipdb; ipdb.set_trace()
    template_path = os.path.join(os.path.dirname(__file__), "page_template.html")
    with open(template_path, "r") as f:
        template = Template(f.read())
    html = template.render(**pack)
    os.makedirs(os.path.dirname(output_html_path), exist_ok=True)
    with open(output_html_path, "w") as f:
        f.write(html)
    print(f"Generated {output_html_path}")

def render_index(page_urls, output_html_path):
    template_path = os.path.join(os.path.dirname(__file__), "index_template.html")
    with open(template_path, "r") as f:
        template = Template(f.read())
    html = template.render(page_urls=page_urls)
    with open(os.path.join(os.path.dirname(__file__), "index.html"), "w") as f:
        f.write(html)
    print(f"Generated {output_html_path}")

def make_html(settings):

    page_urls = []
    for args in settings:
        video_groups = get_video_groups(args["root_group"])
        pack = prepare_render_dict(args, video_groups, os.path.dirname(__file__))
        render_html(pack, os.path.join(os.path.dirname(__file__), args['name'] + ".html"))
        page_urls.append(args['name'] + ".html")
    render_index(page_urls, os.path.join(os.path.dirname(__file__), "index.html"))

make_html(settings)
