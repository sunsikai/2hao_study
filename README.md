# 2号培训外挂-刷课程视频进度、打卡、练习，刷直播视频进度、打卡

> 由于公司从某个地方申请了补贴，需要员工在2号培训APP上进行课程学习。
> 员工每学习一门课，地方会补贴公司三四十块钱，钱方面是与员工没什么关系了。
> 但是课程还是需要员工本人去看才行，而且是强制的，这点就有点狗了。
> 课程学习过程中需不定时人脸打卡，一旦漏打卡或者打卡失败，课程视频就需要重新看。此外课后还需要做练习题。



### 脚本功能介绍：
1. 课程视频打卡。（不需要人脸识别）
2. 课程视频进度保存。（注意，每门课不要一次性刷全完，理由详见后续说明）
5. 自动完成课程的练习。
7. 直播回放视频打卡。
8. 直播回放视频进度保存。。

![功能界面](https://upload-images.jianshu.io/upload_images/23466769-3404adb15b4a69a3.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/600)




### 使用说明如下：

- “2号培训课程学习脚本.exe”和“配置文件.json”放在同一个目录下才能运行

- 初次使用此脚本，需要先绑定账号，输入指令 1（每次输入完数据，回车执行），之后按照窗口提示，进行绑定账号

- 绑定完账号，更新学习计划(如果是直播回放，则不用更新学习计划，请使用其他指令)，按指令2操作（学习计划的状态类型有“已完成”和“进行中”，根据实际情况更新（可上app看学习计划在哪个分类，如下图）） ![团队学习计划-已完成状态下存在有多个学习计划](https://upload-images.jianshu.io/upload_images/23466769-f9883cce4e76ddcf.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/500) ![如有多个学习计划，则需要手动选择更新其中的一个学习计划](https://upload-images.jianshu.io/upload_images/23466769-26d64da6267547ab.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/600)


- 课时视频保存进度、打卡功能，都需要输入“视频ID”字段，该字段值在“配置文件.json”里面可以找到。（这就是需要先更新学习计划的原因）

- 关于“课程视频进度保存”指令功能的使用**注意事项**：假如一门课程下只有一个视频，建议第一次保存进度时，不要直接输入保存进度比例为100，可以先输入1，即将视频的进度刷到1%。隔个几个小时之后再来刷一次，就可以刷100进度。原因是，假如该课程视频第一次保存进度时就直接刷到100，那么在学习课程完毕后，后台记录显示课程开始学习时间和结束时间间隔过短，如下图。（课程的开始学习时间和结束学习时间，是针对于课程而言。如果一门课程下有多个视频，则可先刷一个视频进度到100，等待几小时后再刷其他视频进度到100） ![一次性直接将整门课程刷完导致的后果](https://upload-images.jianshu.io/upload_images/23466769-d6fac59a6240c0b8.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

- 首次更新直播回放信息时，需要有二维码照片（后续再重复更新该直播信息时，则可不用输入二维码图片地址，除非更新的是其他的直播信息），则可如下：![更新直播信息指令](https://upload-images.jianshu.io/upload_images/23466769-2cbdb4f2d8ef6bfa.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/600) ![二维码照片例子](https://upload-images.jianshu.io/upload_images/23466769-d2d7a8640e66f3e7.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/200)

- 直播回放视频打卡指令。需要输入“打卡编号”，此编号在前面指令‘更新直播信息’后，可以在配置文件.json里面找到。用户可根据“是否有打卡”字段判断是否需要进行打卡。如果没输入打卡编号就直接回车，程序会默认在配置文件里面找到所有没打卡的记录，逐个进行打卡。![需打卡信息-打卡编号](https://upload-images.jianshu.io/upload_images/23466769-35ee6529d3ce7508.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/400)

- 直播回放视频进度保存指令。用户可输入视频的时长秒数进行进度保存（可先用手机app扫码看看视频有多长，记得看完秒数后把视频给关闭了）。如果用户没输入要保存的进度秒数就直接回车，程序将默认按照直播计划的时间差秒数进行进度保存（直播计划时间和实际直播时间多多少少会有出入）。刷进度时，不要一次就把视频进度刷满，原因也是为了防止视频的开始学习时间，和结束学习时间间隔过近。

- 无论是课程视频进度保存或是直播回放视频保存，刷进度前，请确保手机没在放视频。刷进度后，请不要立即打开手机课程视频，可稍等个一小会（几十秒即可）再打开手机视频。

- 用户在更新学习计划或直播计划后，数据全都保存在本地的‘配置文件.json’，用户可打开该文件查看下数据是否正常，此脚本无后门。 

- 目前脚本对于异常的操作数据没有做太多的校验处理，如果出现录入数据异常，导致窗口闪退，或者指令数据输错了想要重新输入再来，直接将窗口关闭了重新打开脚本窗口即可。

> [2号培训-项目地址](https://github.com/sunsikai/2hao_study/dist)
> 补充：程序在dist文件夹的dist.zip压缩包里面，直接将压缩包下载后解压就可以用。（window）
