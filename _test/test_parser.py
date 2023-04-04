end_note = """
%0 Journal Article
%A 常远
%A 盖孟
%+ 北京大学信息科学技术学院;北京大学北京市虚拟仿真与可视化工程研究中心;
%T 基于神经辐射场的视点合成算法综述
%J 图学学报
%D 2021
%V 42
%N 03
%K 基于图像的绘制;视点合成;神经辐射场;神经渲染;深度学习
%X 基于图像的视点合成技术在计算机图形学与计算机视觉领域均有广泛的应用,如何利用输入图像的信息对三维模型或者场景进行表达是其中的关键问题。最近,随着神经辐射场这一表示方式的提出,大量基于此表示方法的研究工作对该方法进行了进一步优化和扩展,在准确性、高效性等方面取得了良好的成果。该类研究工作可以根据研究目的大致分为两大类:对神经辐射场算法本身的分析以及优化,和基于神经辐射场框架的扩展及延伸。第一类研究工作对神经辐射场这一表示方法的理论性质和不足进行了分析,并提出了优化的策略,包括对合成精度的优化、对绘制效率的优化以及对模型泛用性的优化。第二类研究工作则以神经辐射场的框架为基础,对算法进行了扩展和延伸,使其能够解决更加复杂的问题,包括无约束拍摄条件下的视点合成、可进行重光照的视点合成以及对于动态场景的视点合成。在介绍了神经辐射场模型提出的背景之后,对以其为基础的其他相关工作按照上述分类进行了讨论和分析,最后总结了神经辐射场方法面对的挑战和对未来的展望。
%P 376-384
%@ 2095-302X
%L 10-1034/T
%U https://kns.cnki.net/kcms/detail/10.1034.T.20210603.0844.002.html 
%W CNKI
"""

from resbibman.core.refparser import endnote

parser = endnote.EndnoteParser()
res = parser.parseEntry(end_note)
print(res)

from resbibman.core.bibReader import BibConverter

conv = BibConverter()
res = conv.fromEndNote(end_note)
print(res)