<template>
  <div class="test">{{ msg }}</div>
</template>

<script>
export default {
  name: "Test",
  props: {
    msg: String,
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
