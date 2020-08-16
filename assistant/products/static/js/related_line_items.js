$(function () {
  /* Interface to view the workflow status from the explorer / editor */
  $(".allocate-button").on("click", function (e) {
    e.preventDefault();
    ModalWorkflow({
      url: this.getAttribute("href"),
      onload: {
        chooser: function (modal, jsonData) {
          $(".choose-line").on("click", function (e) {
            modal.loadUrl(this.getAttribute("data-url"));
            return false;
          });
        },
        allocation: function (modal, jsonData) {
          $("#allocation-form").on("submit", function (e) {
            e.preventDefault();
            $.ajax({
              url: this.getAttribute("action"),
              type: "POST",
              data: $(this).serialize(),
            });
            return false;
          });
        },
        choosen: function (modal, jsonData) {
          modal.respond("choosen");
          modal.close();
        },
      },
    });
    return false;
  });
});
