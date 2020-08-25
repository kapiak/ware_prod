module.exports = {
  pages: {
    weblink_channel: {
      // entry for the page
      entry: "src/views/weblink_channel/main.js",
      // the source template
      template: "public/index.html",
      // output as dist/index.html
      filename: "weblink_channel_checkout.html",
      // when using title option,
      // template title tag needs to be <title><%= htmlWebpackPlugin.options.title %></title>
      title: "Custom Order Request"
    }
  }
};
