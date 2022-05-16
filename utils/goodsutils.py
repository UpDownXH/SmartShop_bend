from apps.goods.models import GoodsChannel


def get_categories():
    # 1 查询所有频道 先按group_id排序 group_id相等的按sequence排序
    channels = GoodsChannel.objects.order_by('group_id', 'sequence')
    # 创建一个空字典 存放拼接好的总数据
    categories = {}

    for c in channels:
        # print(c)
        # 1 组装最外层数据
        # 判断group_id如果已经在字典里存在了 就不用执行了
        if c.group_id not in categories:
            categories[c.group_id] = {"channels": [], 'sub_cats': []}

        # 2 组装里面的额channels里的数据
        category = c.category  # 获取每个频道里的分类对象
        categories[c.group_id]['channels'].append({
            "id": category.id,
            "name": category.name,
            "url": c.url,
        })

        # 3  组装2级和3级分类数据
        category2 = category.subs.all()  # 获取所有的2级分类
        for c2 in category2:

            category3 = c2.subs.all()  # 获取所有的3级分类
            sub_cats3 = []  # 存放所有3级分类的数据
            for c3 in category3:
                sub_cats3.append({
                    'id': c3.id,
                    'name': c3.name
                })

            categories[c.group_id]['sub_cats'].append({
                "id": c2.id,
                'name': c2.name,
                'sub_cats': sub_cats3
            })

    return categories


def get_breadcrumb(category):
    """
    获取面包屑导航
    :param category: 商品类别
    :return: 面包屑导航字典
    """
    breadcrumb = dict(
        cat1='',
        cat2='',
        cat3=''
    )
    if category.parent is None:
        # 当前类别为一级类别
        breadcrumb['cat1'] = category.name
    elif category.subs.count() == 0:
        # 当前类别为三级
        breadcrumb['cat3'] = category.name
        breadcrumb['cat2'] = category.parent.name
        breadcrumb['cat1'] = category.parent.parent.name
    else:
        # 当前类别为二级
        breadcrumb['cat2'] = category.name
        breadcrumb['cat1'] = category.parent.name

    return breadcrumb


"""
规格选项

sku_id 16
sku对象  sku.spu  获取到spu对象  spu对象.specs 能获取到所有的规格   根据规格能获取到所有的选项

sku对象能获取到sku的具体规格

"""
def get_goods_specs(sku):

    # 构建当前商品的规格键
    # 只获取当前的sku的规格   颜色和版本
    sku_specs = sku.specs.order_by('spec_id')
    sku_key = []  # 当前商品的规格的选项id
    print('当前商品的每个规格的选项，放到一个列表sku_key里')
    for spec in sku_specs:
        sku_key.append(spec.option.id)
        print(spec.option.value, end='---')

    print('----sku_key----------------------------:', sku_key)  # 存的是  曜石黑和 128g的id

    # 获取当前商品对应的spu下的所有SKU
    skus = sku.spu.sku_set.all()
    # 构建不同规格参数（选项）的sku字典
    spec_sku_map = {}
    for s in skus:
        # 获取sku的规格参数
        s_specs = s.specs.order_by('spec_id')
        # 用于形成规格参数-sku字典的键
        key = []
        for spec in s_specs:
            key.append(spec.option.id)
        # 向规格参数-sku字典添加记录
        spec_sku_map[tuple(key)] = s.id  # {  (曜石黑,128GB):1,(2b红,64GB):2,(钻雕蓝,64GB):12 }

    print('spec_sku_map=',spec_sku_map)


    # 以下代码为：在每个选项上绑定对应的sku_id值
    # 获取当前商品的规格信息
    goods_specs = sku.spu.specs.order_by('id')
    # 若当前sku的规格信息不完整，则不再继续
    if len(sku_key) < len(goods_specs):
        return


    for index, spec in enumerate(goods_specs):

        # 复制当前sku的规格键
        key = sku_key[:]   # 【颜色id   版本id】

        # 该规格的选项
        spec_options = spec.options.all()

        print(index, '---', spec, '----', 'spec_options=',spec_options)
        for option in spec_options:  #【64  128】
            # 在规格参数sku字典中查找符合当前规格的sku
            key[index] = option.id
            option.sku_id = spec_sku_map.get(tuple(key))

        spec.spec_options = spec_options

    return goods_specs
