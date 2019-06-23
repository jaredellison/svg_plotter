# Notes

[x] Read through existing codebase.
  [x] Diagram code

[x] Split into modules
  [x] Research conventions

[x] Sketch out OOP model (graph and traces are objects)

## Additional
[ ] Refactor README.md to include usage notes from source

## Refactoring ideas
[x] Factor out color functions into separate module
  - angle_to_hex_triplet
  - get_trace_color

[x] Put all config variables in one place

[x] Create method draw_traces from plot_path

[x] Should x,y pairs be tuples?
  - sgv size, graph size, graph offset

[ ] Decouple draw_h_lines and draw_v_lines from functions to figure out lable positions



### Functions

#### Plotting
- log_scale
  - Maps a (freq, amp) coordinate pair to (x, y)

#### Rendering
- draw_point
  - Draws an (x,y) point the graph

- draw_background
  - Draws a rectangle behind the plotting area

- draw_h_lines
  - Draws horizontal markers

- draw_h_lines
  - Draws horizontal markers

- draw_label

- add_v_labels

- add_h_labels

- draw_axis_lable

#### Color
- angle_to_hex_triplet
- get_trace_color

### Main Action

1. Create a dwg object
1. Add groups to the dwg object (shapes, trace, scale_lines, line_labels)
1. Add clip mask to bound traces
1. Establish trace colors
1. Render graph
  1. Background
  1. Vertical and horizontal lines
  1. Axis labels
  1. Clip mask
  1. Use bspline_maker module to get curves from dataset using log scaled points
1. Save output file

### Proposed Higher Level Action

1. Prompt for output name
1. Prompt for input files
1. Prompt for optional parameters
1. Initialize graph object with parameters
1. Attach traces to graph based on input files
1. Render Graph
1. Save output file
