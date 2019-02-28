var vm = new Vue({
    el: '#app',
    data: {
        page: 1,
        // 列表商品
        goods_list: [],
        // 排序字段
        ordering: 'create_time',
        // 当前类别
        category: null,
        category_id: null,
    },

    mounted: function () {

        this.get_current_category();
        this.get_list_goods();
    },

    methods: {
        // 获取商品列表数据

        get_list_goods: function () {
            // 拼接请求的查询字符串的值
            let query_string = window.location.search;
            if (query_string !== null) {
                query_string += '&ordering=' + this.ordering;
            } else {
                query_string = '?ordering=' + this.ordering;
            }
            query_string=query_string.replace("?","");
			//发送请求
            axios.get('http://127.0.0.1:8000/goods/list/'+query_string+'/')
                .then(response => {

                    this.goods_list = response.data['category_goods']['goods_list'];
                    // alert(this.goods_list);

                })
                .catch(error => {
                    console.log("");
                })

        },

        // 获取当前显示的类别
        get_current_category: function () {
            // 获取url中的类别id
            this.category_id = this.get_query_string('category');
            //发送请求
            this.category_id=this.category_id.replace("?","");
            axios.get('http://127.0.0.1:8000/goods/list/'+'category='+this.category_id+'&ordering='+this.ordering+'/')
                .then(response => {
                    this.category = response.data['category_goods'];
                    // alert(this.categories);

                })
                .catch(error => {
                    console.log("");
                })

        },

        // 获取url路径参数
        get_query_string: function(name){
            var reg = new RegExp('(^|&)' + name + '=([^&]*)(&|$)');
            var r = window.location.search.substr(1).match(reg);
            if (r != null) {
                return decodeURI(r[2]);
                // alert(r)
            }
            return null;
        },

        // 排序操作
        on_sort: function(ordering){
            if (ordering !== this.ordering) {
                this.page = 1;
                this.ordering = ordering;
                this.get_list_goods();
            }
        },
    }
});

