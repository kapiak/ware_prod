$(function () {
  /* Interface to view the workflow status from the explorer / editor */
  $(".orders-button").on("click", function (e) {
    e.preventDefault();
    ModalWorkflow({
      url: this.getAttribute("href"),
      onload: {
        /* Object with the keys representing the actions to map
         *
         * */
        chooser: function (modal, jsonData) {
          /* some sumbit which returns false */
          $(".paginate").on("click", function (e) {
            e.preventDefault();
            let url =
              this.getAttribute("href") +
              "?page=" +
              this.getAttribute("data-page");
            $.ajax({
              url: url,
              processData: false,
              contentType: false,
              type: "GET",
              dataType: "text",
              success: modal.loadResponseText,
            });

            return false;
          });
        },
        choosen: function (modal, jsonData) {
          /* pass thre esponse from this onload to responses */
          modal.respond(
            "choosen",
            jsonData["embed_html"],
            jsonData["embed_data"]
          );
          modal.close();
        },
      },
      responses: {
        choosen: function (resData) {
          console.log("Yup");
          modal.close();
        },
      },
    });
    return false;
  });
});
