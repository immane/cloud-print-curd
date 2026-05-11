<script>
export default {
  onLaunch() {
    console.log('Cloud Print mini app launched');
  }
};
</script>

<style>
page {
  background: linear-gradient(180deg, #17c78c 0%, #c9f1df 24%, #ffffff 60%);
  color: #171717;
  font-family: 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

view,
text,
button {
  box-sizing: border-box;
}

button::after {
  border: 0;
}
</style>
