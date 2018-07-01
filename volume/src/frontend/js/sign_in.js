var signIn = new Vue({
  el: '#SignIn',
  data: {
    id: '',
    pw: ''
  },
	created () {
    store.account.id = '';
    store.account.level = '';
    store.account.accessToken = '';
    store.account.refershToken = '';
  },
  methods: {
		signIn () {
      axios({
        url: "/skp/v1/tokens",
        method: "post",
        data: {
          'id' : this.id,
          'pw' : this.pw
        }
      })
      .then((response) => {
        var data = response['data'];
        console.log(response);
        store.account.id = data['id'];
        store.account.level = data['level'];
        store.account.accessToken = data['access_token'];
        store.account.refershToken = data['refresh_token'];
        window.location.href = '/index.html';
      })
      .catch((response) => {
        console.log(response);
      });
    },
  }
});
