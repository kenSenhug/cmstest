var vm = new Vue({
    el: '#app',
    data: {
        messages: [1,2,3],
        carousel_news: [],
        recommended_news: [],
        picture_news: [],
        category_query_list: [],
        data_list: []
    },

    mounted: function () {
        this.init_top_news();
        this.init_category_news();
    },

    methods: {
        // 初始化显示顶部的新闻数据
        init_top_news: function () {
           axios.get('http://127.0.0.1:8000/topnews/')
               .then(response=>{
                   console.log(response.data);
                   vm.carousel_news = response.data.carousel_news;
                   vm.recommended_news = response.data.recommended_news;
                   vm.picture_news = response.data.picture_news;
               })
               .catch(error=>{
                   console.log(error.response)
               })
        },

        // 初始化显示类别新闻数据
        init_category_news: function () {
           axios.get('http://127.0.0.1:8000/categorynews/')
               .then(response=>{
                   console.log(response.data);
                   vm.data_list = response.data.data_list;
                   // vm.category_query_list = response.data.category_query_list;
               })
               .catch(error=>{
                   console.log(error.response)
               })
        },
    },

    filters: {
        formatDate: function (time) {
            return dateFormat(time, "yyyy-mm-dd");
        },

        formatDate2: function (time) {
            return dateFormat(time, "yyyy-mm-dd HH:MM:ss");
        },
    },

    // 数据发生改变并渲染刷新完成后调用
    updated: function () {
        // 界面刷新后开始轮播
        $("#focus-box").flexslider({
            directionNav: false,
            pauseOnAction: false
        });
    }
});
