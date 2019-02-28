
# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from goods import serializers
from goods.models import Goods, GoodsCategory, GoodsAlbum
from goods.serializers import GoodsCategoriesSerializer, GoodsIndexCategorySerializer, GoodsDetailSerializer, \
    GoodspictureSerializer


# 右侧的推荐


class GoodsCommendView(APIView):
    def get(self, resquest):
        red_goods = Goods.objects.filter(is_red=1).exclude(status=1)[0:4]
        red_goods = serializers.GoodsSerializer(red_goods, many=True).data
        data = {
            'red_goods': red_goods,
        }
        return Response(data)

    # filter_backends = (DjangoFilterBackend, OrderingFilter)


# 首页的类别商品展示
class CategoriesGoodsView(APIView):
    def get(self, request):

        category_list = []
        category = GoodsCategory.objects.filter(parent_id=0).all()
        for i in category:
            category_id = []
            goods_category = GoodsCategory.objects.filter(parent=i.id)
            a = GoodsCategoriesSerializer(goods_category, many=True).data
            for j in a:
                category_id.append(j.setdefault('id'))
            print(category_id)
            x = GoodsCategoriesSerializer(i).data
            x['goodscategory_set'] = a
            goods = Goods.objects.filter(category_id__in=category_id).exclude(status=1).order_by('-sales')[0:5]
            b = GoodsIndexCategorySerializer(goods, many=True).data
            x['goods'] = b
            category_list.append(x)
        data = {
            'category_list': category_list,
        }
        return Response(data)


class CategoryView(APIView):
    def get(self, request, pk=None, order=None):
        category = GoodsCategory.objects.filter(id=pk)[0]
        end_order = '-' + order
        if end_order.count('-') == 2:
            end_order = order.replace("-", "")
        # print(order)
        a = GoodsCategoriesSerializer(category).data
        # print(a)
        if a.setdefault('parent') == 0:
            category_id = []
            goods_category = GoodsCategory.objects.filter(parent=pk).all()
            b = GoodsCategoriesSerializer(goods_category, many=True).data
            for j in b:
                category_id.append(j.setdefault('id'))
            # print(category_id)
            goods = Goods.objects.filter(category_id__in=category_id).exclude(status=1).order_by(end_order).all()
            # print(goods)
            a['goods_list'] = GoodsIndexCategorySerializer(goods, many=True).data
        else:
            a['parent'] = GoodsCategoriesSerializer(GoodsCategory.objects.filter(id=a.setdefault('parent'))[0]).data
            a['goods_list'] = GoodsIndexCategorySerializer(Goods.objects.filter(category_id=pk).exclude(status=1).order_by(end_order).all(), many=True).data
        data = {
            'category_goods': a,
        }
        return Response(data)


class GoodsDetailView(APIView):
    def get(self, request, pk=None):
        goods = Goods.objects.filter(id=pk)[0]
        goods_dict = GoodsDetailSerializer(goods).data
        goods_dict['goodsalbum_set'] = GoodspictureSerializer(GoodsAlbum.objects.filter(goods=pk).all(), many=True).data
        cat2 = GoodsCategory.objects.filter(id=goods_dict.setdefault('category'))[0]
        cat2 = GoodsCategoriesSerializer(cat2).data
        cat1 = GoodsCategory.objects.filter(id=cat2.setdefault('parent'))[0]
        cat2['parent'] = GoodsCategoriesSerializer(cat1).data
        goods_dict['category'] = cat2
        data = {
            'goods': goods_dict,
        }
        return Response(data)
