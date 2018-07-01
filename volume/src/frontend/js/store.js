Vue.use(vuejsStorage);

const store = new Vue({
  data: {
    account: {
      id: '',
      level: '',
      accessToken: '',
      refershToken: ''
    },
  },
  storage: {
    keys: [
      'account.id',
      'account.level',
      'account.accessToken',
      'account.refershToken'
    ],
    storage: sessionStorage,
    namespace: 'StKildaPierStorage'
  },
  created () {
  },
  methods: {
    refershToken() {
      if (!this.account.refershToken) {
        window.location.href = '/sign_in.html';
      }

			axios({
        url: "/skp/v1/tokens",
        method: "put",
        headers: {
          'Authorization' : "Bearer " + this.account.refershToken
        }
      })
      .then((response) => {
        var data = response['data'];
        console.log("refershToken: SUCCESS");
        console.log(response);
        this.account.accessToken = data['access_token'];
      })
      .catch((response) => {
        console.log("refershToken: FAIL");
        console.log(response);
        window.location.href = '/index.html';
      })
		}
  }
});
