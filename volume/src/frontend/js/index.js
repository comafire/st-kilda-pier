var index = new Vue({
  el: '#Index',
  data: {
    id: '',
    level: '',
    accessToken: '',
    refershToken: ''
  },
  created () {
    this.id = store.account.id;
    this.level = store.account.level;
    this.accessToken = store.account.accessToken;
    this.refershToken = store.account.refershToken;
  },
  methods: {
  }
});
