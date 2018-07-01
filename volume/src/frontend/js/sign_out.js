var signOut = new Vue({
  el: '#SignOut',
  data: {
  },
	created () {
    store.account.id = '';
    store.account.level = '';
    store.account.accessToken = '';
    store.account.refershToken = '';
    window.location.href = '/index.html';
  },
  methods: {
  }
});
