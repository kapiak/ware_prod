const app = new Vue({
  el: "#app",
  delimiters: ["${", "}"],
  data: {
    userEmailExists: false,
    errors: [],
    totalForms: 1,
    initialForms: 0,
    minNumForms: 0,
    maxNumForms: 1000,
    csrfmiddlewaretoken: csrfToken,
    form: {
      customer_form: {
        name: "",
        email: "",
        city: "",
        state: "",
        country: "",
        code: "",
      },
      shipping_form: {
        method: "DHL",
        weight: 0,
      },
      product_add_formset: [
        {
          url: "",
          name: "",
          quantity: 0,
          price: 0,
          comments: "",
        },
      ],
    },
  },
  methods: {
    addProduct: function () {
      this.form.product_add_formset.push({
        url: "",
        name: "",
        quantity: 0,
        price: 0,
        comments: "",
      });
      this.totalForms = this.form.product_add_formset.length;
    },
    removeProduct: function (index) {
      this.form.product_add_formset.splice(index, 1);
      this.totalForms = this.totalForms - 1;
    },
    checkout: function () {
      http
        .post(checkoutAPI, this.form)
        .then((res) => {
          console.log(res);
          window.location.href = successURL;
        })
        .catch((err) => console.log(err));
    },
  },
  computed: {
    userEmail() {
      return this.form.customer_form.email;
    },
  },
  watch: {
    userEmail(val) {
      http
        .get(`/users/exists/${val}`)
        .then((res) => {
          this.userEmailExists = res.data.exists;
        })
        .catch((err) => console.log(err));
    },
  },
});
