import pkg_resources
import sys
for p in ("dash", "dash_renderer", "dash_core_components",
          "dash_html_components", "dash_table"):
    print(p, pkg_resources.get_distribution(p).version)
