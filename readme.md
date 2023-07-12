# CLICC Signage dynamic hours repo

This code repo use frontend techniques to create an embedded html file for RiseVision display. Same techniques can be use for all dynamic rendering scenarios on RiseVision.

## RiseVision limitation

- All `http` must be changed to `https`, even just for pattern matching without actual internet request.

- Only one html file is supported for each presentation. css and js files need to be internal.

- To avoid repeated image loading, all pngs and svgs are also embedded into html (pngs are embedded as binary files)

- While displaying the html file, you need to make sure RiseVision reload the page at a resonable rate (at least once a day for library hours). This could be done by looping through different presentations or by setting a refresh time.

## File structure

- \branding: branding pdf with color info, etc.

- \images: all the images used in html.

- \src: all the source code. Here scss is used to facilitate variables.

  - \horizontal: the original render size is 768px \* 432px. When the scaling factor is set to 5, it's 3840px \* 2160px. If the scaling factor is 2.5, it's 1920px \* 1080px.

  - \vertical: width and height flipped.

## How to maintain the code

- Non-styling issues: It's recommended to edit the `<script></script>` in the html files directly. You can easily edit the `API_URL` or `locationIds`.

  To edit the rest of the file, you need to have basic Javascript knowledge. This code should be stable unless Libcal make any breaking updates on their API/Widgets.

- Styling issues: You need to have basic css knowledge. It's recommended to edit the `<style></style>` in the html files directly. Or you can edit the variables in scss, watch it and then inject to html again.
