任务：

根据 analysis 文件生成所有业务配置。



输入：

analysis/{site}.md



要求：


针对每个一级分类：

  直接在 `result/{site}/` 目录下生成平铺的 `<category>.py` 文件（不创建子目录）。


例如：


result/hainan/


    government_purchase/

        caigougonggao.py

        chengjiaogonggao.py



    engineering/

        zhaobiaogonggao.py


    property_trade/

        chengjiao.py

