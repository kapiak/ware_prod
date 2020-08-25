<template>
  <div id="app">
    <Test msg="Test Component" />
  </div>
</template>

<script>
import Test from "../../components/Test.vue";

export default {
  name: "App",
  components: {
    Test,
  },
};
</script>

<style>
</style>
