var vm = new Vue({
    el: '#app',
    data: {
        host: 'http://127.0.0.1:8000',
        goods_list: [],         // 购物车中的商品
        origin_input: 1,        // 商品数量
    },

    computed: {
        select_all: function() {
            for (let i = 0; i < this.goods_list.length; i++) {
                let goods = this.goods_list[i];
                // 重新计算小计金额, 自动刷新界面显示
                if (!goods.selected) {
                    return false;
                }
            }
            return true;
        },

        // 获取选中的商品的数量
        selected_count: function() {
            let total_count = 0;
            for (let i = 0; i < this.goods_list.length; i++) {
                let goods = this.goods_list[i];
                // 重新计算小计金额, 自动刷新界面显示
                goods.amount = parseFloat(goods.sell_price) * parseInt(goods.count);
                if (goods.selected) {
                    total_count += parseInt(goods.count);
                }
            }
            return total_count;
        },

        // 获取选中的商品的总金额
        selected_amount: function() {
            let total_amount = 0;
            for (let i = 0; i < this.goods_list.length; i++) {
                let goods = this.goods_list[i];
                if (goods.selected) {
                    total_amount += parseFloat(goods.sell_price) * parseInt(goods.count);
                }
            }
            // 金额保存两位有效数字
            return total_amount.toFixed(2);
        },
    },

    mounted: function () {
        this.get_cart_goods();
    },

    methods: {
        // 全选和全不选
        on_selected_all: function(){
            var selected = !this.selected_all;
            // 发请求保存商品的勾选状态
            var data = {
                selected: selected
            };
            axios.put(this.host + '/cart/selection/', data, {
                    responseType: 'json',
                    headers:{
                        'Authorization': 'JWT ' + this.token
                    },
                    withCredentials: true // 跨域请求传递cookie给服务器
                })
                .then(response => {
                    // 设置商品全选或全不选
                    for (var i=0; i<this.goods_list.length;i++){
                        this.goods_list[i].selected = selected;
                    }
                })
                .catch(error => {
                    console.log(error.response.data);
                })
            },

        // 获取购物车商品数据
        get_cart_goods: function () {
           axios.get(this.host + '/cart/')
            .then(response => {
                this.goods_list = response.data;

                // 计算每件商品的小计金额: 小计金额 amount = 单价 * 数量
                for (var i = 0; i < this.goods_list.length; i++) {
                    this.goods_list[i].amount = (parseFloat(this.goods_list[i].price)
                        * this.goods_list[i].count).toFixed(2);  // toFixed： 保留两位小数点
                }
            })
            .catch(error => {
                console.log(error.response.data);
            })
        },

        // 点击增加购买数量
        on_add: function(index) {
            let goods = this.goods_list[index];
            let count = parseInt(goods.count) + 1;

            this.update_cart_count(goods.id, count, index);
        },

        // 点击减少购买数量
        on_minus: function(index){
            let goods = this.goods_list[index];
            let count = parseInt(goods.count);
            if (count > 1) {
                count--;
                this.update_cart_count(goods.id, count, index);
            }
        },

        // 更新购物车商品购买数量
        on_input: function(index) {
            // 输入的数量不能超过最大库存
            let goods = this.goods_list[index];
            this.update_cart_count(goods.id, goods.count, index);
        },

        // 更新购物车商品数量
        update_cart_count: function(goods_id, count, index) {

            //发送请求
            axios.put(this.host+'/cart/', {

                    goods_id: this.goods_list[index].id,
                    count: count,
                    selected: this.goods_list[index].selected
                }, {
                    headers:{
                        'Authorization': 'JWT ' + this.token
                    },
                    withCredentials: true
                })
                .then(response => {
                    this.goods_list[index].count = response.data.count;
                })
                .catch(error => {
                    if ('non_field_errors' in error.response.data) {
                        alert(error.response.data.non_field_errors[0]);
                    } else {
                        alert('修改购物车失败');
                    }
                    console.log(error.response.data);
                })
        },

        // 删除购物车中的一个商品
        delete_goods: function(index){
            //发送请求
            var config = {
                data: {  // 注意：delete方法参数的传递方式
                    sku_id: this.goods_list[index].id
                },
                headers:{
                    'Authorization': 'JWT ' + this.token
                },
                withCredentials: true
            }
            axios.delete(this.host+'/cart/', config)
                .then(response => {
                    // 删除数组中的下标为index的元素
                    this.goods_list.splice(index, 1);
                })
                .catch(error => {
                    console.log(error.response.data);
                })
        },

        // 清空购物车
        clearCart: function(index){
            //发送请求
        },
    }
});