#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = '孙思锴'

from datetime import datetime
from random import randint
import requests
import json
import time
from zxing import BarCodeReader
from os import path
import urllib.parse

# 关闭警告
requests.packages.urllib3.disable_warnings()
# 请求重试次数
requests.adapters.DEFAULT_RETRIES = 5
session = requests.session()
session.keep_alive = False

global dic  # 配置字典 配置文件.json


def update_dict(newDict={}):
    # 更新配置文件字典
    with open(file='配置文件.json', mode='r', encoding='UTF-8') as fp:
        oldDict = json.load(fp)
    oldDict.update(newDict)
    with open(file='配置文件.json', mode='w', encoding='UTF-8') as fp:
        json.dump(oldDict, fp, indent=4, ensure_ascii=False)
    return oldDict


def send_code(account=''):
    """
    发送验证码
    :param account:账号（手机号）
    :return: null
    """
    url = "https://api.2haohr.com/person_ucenter_auth/mobile_login/get_checkcode/?mobile=" + account + "&voice=0"
    result = session.get(url=url, verify=False).json()
    print('请求发送验证码结果：', result)


def get_token(account='', code=''):
    """
    发送验证码，accesstoken（用于后续所有请求）
    :param account:账号（手机号）
    :param code:验证码
    :return: null
    """
    url = "https://api.2haohr.com/person_ucenter_auth/mobile_login/get_token/?mobile=" + account + "&checkcode=" + code + "&app_id=2014&account_app_id=1014"
    result = session.get(url=url, verify=False).json()
    print('获取token的请求结果：', result)
    if result['result']:
        timeStamp = float(result['data']['expire_date'] / 1000)
        otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timeStamp))
        update_dict({"accesstoken": result['data']['accesstoken'], "account": account, 'token过期时间': otherStyleTime})
        print('手机号：', account, '绑定成功，token有效时长：', otherStyleTime)
    else:
        print('手机号绑定失败，请重新进行绑定。失败提示：', result['errormsg'])


dic = update_dict()


def getTeamPlan(planStatus='1'):
    """
    获取学习任务
    :param planStatus:计划完成状态，1、进行中；2、已完成
    :return: null
    """
    url = 'https://api.2haohr.com/training/person/learning/plan/team/list?planStatus=' + planStatus + '&limit=100&p=1'
    result = session.get(url=url, headers={"accesstoken": dic['accesstoken']}, verify=False).json()
    # print('获取学习计划请求结果：', result)

    if result['data']["total_count"] == 0:
        print('当前计划状态下查无相关学习计划，重新查询其他学习计划')
        update_dict({"learningPlanId": '', "课程信息": []})
    elif result['data']["total_count"] == 1:
        plan = result['data']["objects"][0]
        update_dict({"learningPlanId": plan['id'], '学习计划名称': plan['planName'], '课程数量': plan['courseNum'],
                     '总课时': plan['allClassHourse']})
        print('已更新课程学习计划如下>>>>>>', '学习计划id：', plan['id'], '\t名称：', plan['planName'], '\t课程数量：', plan['courseNum'],
              '\t总课时：', plan['allClassHourse'])
    else:
        print('监测到存在多个学习计划，相关信息如下：')
        for plan in result['data']["objects"]:  # 输出查询到的学习计划学习
            print('学习计划id：', plan['id'], '\t名称：', plan['planName'], '\t课程数量：', plan['courseNum'], '\t总课时：',
                  plan['allClassHourse'])

        planID = input('请输入要更新的学习计划ID：')
        for plan in result['data']["objects"]:
            if planID == plan['id']:
                update_dict({"learningPlanId": plan['id'], '学习计划名称': plan['planName'], '课程数量': plan['courseNum'],
                             '总课时': plan['allClassHourse']})
                print('已更新课程学习计划如下>>>>>>', '学习计划id：', plan['id'], '\t名称：', plan['planName'], '\t课程数量：',
                      plan['courseNum'],
                      '\t总课时：', plan['allClassHourse'])
                break
        else:
            print('更新学习计划失败！查无此学习计划id！')
            update_dict({"learningPlanId": '', "课程信息": []})


def getSectionList(courseId=''):
    """
    获取课程的视频IP
    :param courseId: 课程id
    :return: sectionList
    """
    url = "https://api.2haohr.com/training/person/course/sectionList?learningPlanId=" + dic[
        'learningPlanId'] + "&courseId=" + courseId + "&p=1&limit=999"

    result = session.get(url=url, headers={"accesstoken": dic['accesstoken']}, verify=False).json()
    # print('查询课程视频信息请求结果：', result)
    sectionList = []
    for section in result["data"]["objects"]:
        sectionDic = {"视频ID": section.get("coursewareId", ""), "视频进度(%)": section.get("coursewarePercentage", ""),
                      "视频总长(s)": section.get("totalDuration", ""), "当前观看(s)": section.get("currentDuration", "")}
        sectionList.append(sectionDic)
    return sectionList


def courseList():
    """
    更新所有课程学习
    :return:
    """

    if not dic['learningPlanId']:
        update_dict({"课程信息": []})
        print('更新学习计划失败！')
        return

    url = "https://h5.2haohr.com/api/training/person/learning/plan/team/course/list?learningPlanId=" + dic[
        'learningPlanId'] + "&limit=9999&p=1"
    result = session.get(url=url, headers={"accesstoken": dic['accesstoken']}, verify=False).json()

    print('获取学习计划信息请求结果：', result)
    courseList = []
    for course in result["data"]['objects']:
        courseDic = {"课程名称": course.get("courseName", ''), "课程ID": course.get("courseId", ''),
                     "ID": course.get("id", ''),
                     "课时": course.get("classHour", ''), "课程进度(%)": course.get("percentage", ''),
                     "chapterNum": course.get("chapterNum", ''), "courseChannel": course.get("courseChannel", ''),
                     "courseType": course.get("courseType", ''), "tabSource": course.get("tabSource", ''),
                     }
        courseDic["课程视频"] = getSectionList(courseDic["课程ID"])  # 获取课程内视频信息
        courseList.append(courseDic)
    update_dict({"课程信息": courseList})
    print('更新学习计划课程完成，可打开“配置文件.json”进行查看')


def videoPunch(courseInfo={}, recordId=0, runchNo=''):
    """
    课程视频打卡，包含runchNo则为指定打卡，不包含runchNo值则为随机打卡
    :param courseInfo: 视频相关信息
    :param recordId: 时间戳
    :return:
    """
    url = "https://api.2haohr.com/training/person/randomPunch/punch"
    data = {
        "planCourseId": courseInfo['课程ID'],
        "coursewareId": courseInfo['视频ID'],
        "channelId": "",
        "runchType": 1,
        "runchNo": runchNo,
        "recordId": recordId
    }
    data = json.dumps(data).replace(" ", '')
    result = session.post(url=url, headers={"accesstoken": dic['accesstoken']}, data=data, verify=False).json()
    print('课程视频打卡请求结果', result)


def courseDurationSave(courseInfo={}, recordId=0, currentDuration=0, percentage=0):
    """
    保存课程学习进度（网页端）
    :param courseInfo: 视频信息
    :param recordId: 时间戳 int
    :param currentDuration: 保存秒数 int
    :param percentage: 进度比（1-100）
    :return:
    """
    url = "https://i.2haohr.com/api/training/person/signUp/duration/save"
    data = {
        "ppId": None,
        "parentId": None,
        "channelType": 5,
        "channelId": courseInfo['课程ID'],
        "courseChannel": 1,
        "operationType": 2,
        "percentage": percentage,
        "currentDuration": currentDuration,
        "recordId": recordId,
        "coursewareId": courseInfo['视频ID'],
        "equipmentType": 1
    }
    data = json.dumps(data).replace(" ", '')
    print("保存请求参数>>>>>>进度比：", percentage, "当前秒数", currentDuration)
    result = session.post(url=url, headers={"accesstoken": dic['accesstoken']}, data=data, verify=False).json()
    print("保存请求结果：", result)
    pass


def getPaperToken(channelId=''):
    """
    获取试卷ID信息
    :param channelId:课程的ID，非“课程ID”字段
    :return:{'data': {'paperId': '2089911071686475776', 'tokenUuid': '529a130d317340a29ab87562431aa24f'}, 'errorId': '', 'errormsg': '', 'msg': 'success', 'result': True, 'resultcode': 200}
    """
    url = 'https://api.2haohr.com/training/person/paper/getToken?channelId=' + channelId + '&channelType=4&paperSource=2'
    result = session.get(url=url, headers={"accesstoken": dic['accesstoken']}, verify=False).json()
    print('课程试题ID请求结果：', result)
    return result


def getExamQuestion(paperId=""):
    """
    获取试卷考题
    :param paperId:试卷ID
    :return:试题答案 <list>
    """
    url = 'https://h5.2haohr.com/api/exam/question/list?paperId=' + paperId
    result = session.get(url=url, headers={"accesstoken": dic['accesstoken']}, verify=False).json()
    print('课程试题答案请求结果：', result)
    optionAnswers = []  # 选择题答案
    for question in result['data']['questions']:
        if question['type'] == 4:  # 题目type为4表示单选，14表示多选
            value = ''  # 试题答案
            for option in question['options']:
                if option['isRight']:
                    value = option['id']
                    break
        elif question['type'] == 14:  # 题目type为4表示单选，14表示多选
            value = []  # 试题答案
            for option in question['options']:
                if option['isRight']:
                    value.append(option['id'])
        answer = {"questionId": question['id'], "type": question['type'], "value": value}
        optionAnswers.append(answer)  # 将题目答案添加到list
    return optionAnswers


def examStart(paperId=''):
    """
    请求开始考试
    :param paperId:试卷ID
    :return:
    """
    url = 'https://h5.2haohr.com/api/exam/start'
    data = {'paperId': paperId}
    data = json.dumps(data).replace(' ', '')  # 转换为字符串
    result = session.post(url=url, headers={"accesstoken": dic['accesstoken']}, data=data, verify=False).json()
    print('请求开始考试结果：', result)


def examSubmit(paperAnswer={}):
    """
    请求提交试卷
    :param paperAnswer:试卷答案
    :return:
    """
    url = 'https://h5.2haohr.com/api/exam/submit'
    data = json.dumps(paperAnswer).replace(' ', '')  # 转换为字符串
    result = session.post(url=url, headers={"accesstoken": dic['accesstoken']}, data=data, verify=False).json()
    print('提交试卷请求结果：', result)


def examResult(paperId=''):
    """
    查看试卷结果
    :param paperId:试卷ID
    :return:
    """
    url = 'https://h5.2haohr.com/api/exam/asyncResult?paperId=' + paperId
    result = session.get(url=url, headers={"accesstoken": dic['accesstoken']}, verify=False).json()
    if result['resultcode'] == 200:
        print('查看答卷结果 >>>>>> 成绩:', result['data']['examScore'], '是否通过:', result['data']['isPass'], '错题数:',
              result['data']['wrongNum'], '做题时长:', result['data']['examTime'], '交卷时间:', result['data']['submitTime'])
    else:
        print('查看答卷失败，失败原因：', result)


def getImageScene(imagePath='二维码.jpg'):
    """
    更新二维码照片包含的scene到配置文件
    :param imagePath: 照片地址
    :return: scene 房间地址
    """
    if path.exists(imagePath):
        reader = BarCodeReader()
        barcode = reader.decode(imagePath)
        scene = urllib.parse.parse_qs(urllib.parse.urlparse(barcode.parsed).query)['scene'][0]
        return scene


def getLiveChannelId(scene=''):
    """
    获取直播的channelId()
    :param scene:
    :return:
    """
    url = "https://api.2haohr.com/person_ucenter/api/wechat_mini_program/miniprogram_qrcode_info/?scene=" + scene
    result = session.get(url=url, headers={"accesstoken": dic['accesstoken']}, verify=False).json()
    target = urllib.parse.unquote(result['data']['target'])
    channelId = urllib.parse.parse_qs(urllib.parse.urlparse(target).query)['channelId'][0]
    return channelId


def updateLivePlanInfo(channelId=''):
    """
    获取直播计划学习
    :param channelId:
    :return:
    """
    url = 'https://h5.2haohr.com/api/training/person/livePlan/validate?channelId=' + channelId
    result = session.get(url=url, headers={"accesstoken": dic['accesstoken']}, verify=False).json()
    print('直播信息请求结果', result)

    liveDic = {}
    liveDic['名称'] = result['data']['livePlanName']
    liveDic['计划ID'] = result['data']['livePlanId']
    liveDic['排列ID'] = result['data']['liveArrangeId']
    liveDic['计划开始时间'] = result['data']['startTime']
    liveDic['计划结束时间'] = result['data']['endTime']
    liveDic['channelId'] = channelId

    url = 'https://h5.2haohr.com/api/training/person/randomPunchPoint/getPointList?planType=4&planId=' + \
          liveDic['计划ID'] + '&courseId=' + liveDic['排列ID']
    result = session.get(url=url, headers={"accesstoken": dic['accesstoken']}, verify=False).json()
    print('获取直播打卡信息请求结果', result)

    punchLog = []
    for punch in result['data']:
        punchLog.append({"打卡编号": punch['punchNo'], "是否人脸": punch['hasFace'], "是否有打卡": punch['hasPunch'],
                         "打卡成功": punch['hasPunchSuccess'], "打卡类型": punch['punchType']['value']})
    liveDic['需打卡信息'] = punchLog
    update_dict(newDict={'直播信息': liveDic})


def livePunch(channelId='', runchType=1, runchNo='', recordId=0):
    """
    直播打卡，包含runchNo则为指定打卡
    :param channelId:
    :param runchType:
    :param runchNo:
    :param recordId: 时间戳
    :return:
    """
    url = "https://api.2haohr.com/training/person/randomPunch/punch"
    data = {
        "channelId": channelId,
        "runchType": runchType,
        "runchNo": runchNo,
        "recordId": recordId
    }
    data = json.dumps(data).replace(" ", '')
    result = session.post(url=url, headers={"accesstoken": dic['accesstoken']}, data=data, verify=False).json()
    print('直播回放打卡请求结果', result)


def liveDurationSave(channelId="2087975536100089857", recordId=0, currentDuration=0):
    """
    直播回放进度保存
    :param channelId: 直播ID
    :param recordId: 时间戳 int
    :param currentDuration: 视频进度 秒 int
    :return:
    """
    url = 'https://h5.2haohr.com/api/training/person/livePlan/arrange/duration'
    data = {
        "channelId": channelId,
        "recordId": recordId,  # recordId
        "effective": 1,
        "playback": 1,
        "app": True,
        "currentDuration": currentDuration
    }
    print('请求进度保存参数>>>>>>：时间戳：', recordId, '\t保存时间（秒）：', currentDuration)
    data = json.dumps(data).replace(" ", '')
    result = session.post(url=url, headers={"accesstoken": dic['accesstoken']}, data=data, verify=False).json()
    print('请求进度保存结果：', result)


if __name__ == '__main__':
    print('当前登录账号为：', dic['account'], '\t登录过期时间为：', dic['token过期时间'])
    while True:
        dic = update_dict()
        key = int(input("1：换绑账号；\t2：学习计划更新；\t3：课程视频打卡；\n"
                        "4：课程视频进度保存；\t5：单门课程练习完成；\t6：全部课程练习完成；\n"
                        "7：更新直播回放信息；\t8：直播回放视频打卡；\t9：直播回放视频进度保存；\n"
                        "10：功能测试；\t10：结束程序。\n请输入上述数字指令编号执行对应任务："))

        if key == 1:  # 换绑账号
            account = input('请输入手机号：')
            send_code(account=account)  # 发送验证码
            code = input('请输入验证码：')
            get_token(account=account, code=code)  # 更新 token信息
            pass

        elif key == 2:  # 学习计划更新
            code = input('请输入要更新的学习计划状态指令编号（1：进行中；\t2：已完成。）：')
            getTeamPlan(planStatus=code)  # 获取学习计划ID
            courseList()  # 更新课程信息
            pass

        elif key == 3:  # 课程视频打卡
            coursewareId = input('请输入要进行打卡的视频ID（提示：配置文件.json）：')
            for course in dic['课程信息']:
                for section in course['课程视频']:
                    if section['视频ID'] == coursewareId:
                        courseInfo = section
                        courseInfo['课程ID'] = course["ID"]
                        break
            recordId = int(round(time.time() * 1000))
            videoPunch(courseInfo=courseInfo, recordId=recordId)  # 打卡
            pass

        elif key == 4:  # 课程视频进度保存
            coursewareId = input('请输入要快进的视频ID（提示：ID从配置文件.json文件找）：')
            percentage = int(input('请输入要保存的进度比例（数值范围在：1-100）：'))
            # 从配置文件中获取课程信息
            courseInfo = {}
            for course in dic['课程信息']:
                for section in course['课程视频']:
                    if section['视频ID'] == coursewareId:
                        courseInfo = section
                        courseInfo['课程ID'] = course["ID"]
                        break
            # 开始模拟保存视频进度
            interval = 60 if courseInfo['视频总长(s)'] // 100 > 60 else courseInfo['视频总长(s)'] // 100  # 模拟请求时间间隔
            saveDuration = courseInfo['视频总长(s)'] * percentage // 100  # 最终要保存的秒数
            for currentDuration in range(0, saveDuration, interval):
                recordId = int(time.time() * 1000)  # 时间戳
                currentPercentage = currentDuration * 100 // courseInfo['视频总长(s)']  # 计算要保存进度比
                # 下面会连续发送两个请求，为的是可以计算有效学时
                courseDurationSave(courseInfo=courseInfo, recordId=recordId,
                                   currentDuration=0 if currentDuration == 0 else (currentDuration - interval),
                                   percentage=currentPercentage)
                courseDurationSave(courseInfo=courseInfo, recordId=recordId,
                                   currentDuration=currentDuration, percentage=currentPercentage)

            recordId = int(time.time() * 1000)  # 时间戳
            courseDurationSave(courseInfo=courseInfo, recordId=recordId, currentDuration=saveDuration - interval,
                               percentage=percentage)  # 保存进度100%
            courseDurationSave(courseInfo=courseInfo, recordId=recordId, currentDuration=saveDuration,
                               percentage=percentage)  # 保存进度100%
            print('视频视频进度保存结束！')
            pass

        elif key == 5:  # 单门课程练习完成
            channelId = input('请输入要完成的课程的ID值（提示：配置文件.json，非“课程ID”字段）：')
            result = getPaperToken(channelId=channelId)
            if result['result']:
                paperId = result['data']['paperId']
                tokenUuid = result['data']['tokenUuid']
                optionAnswers = getExamQuestion(paperId=paperId)  # 获取选择题答案
                paperAnswer = {"paperId": paperId, "questions": optionAnswers, "paperToken": tokenUuid}
                examStart(paperId=paperId)  # 请求考试开始
                sleepTime = randint(3, 5)  # 随机等待3-5秒
                print('随机等待', sleepTime, '秒，再进行交卷！')
                time.sleep(sleepTime)
                examSubmit(paperAnswer=paperAnswer)  # 提交试卷
                examResult(paperId=paperId)  # 查看试卷结果
                pass
            else:
                print('查询课程试卷失败，提示信息：', result['errormsg'])
            pass

        elif key == 6:  # 全部课程练习完成
            for course in dic['课程信息']:
                print(course['课程名称'], '课程答卷开始，，，')
                result = getPaperToken(channelId=course['ID'])
                if result['result']:
                    paperId = result['data']['paperId']
                    tokenUuid = result['data']['tokenUuid']
                    optionAnswers = getExamQuestion(paperId=paperId)  # 获取选择题答案
                    paperAnswer = {"paperId": paperId, "questions": optionAnswers, "paperToken": tokenUuid}
                    examStart(paperId=paperId)  # 请求考试开始
                    sleepTime = randint(3, 5)  # 随机等待3-5秒
                    print('随机等待', sleepTime, '秒，再进行交卷！')
                    time.sleep(sleepTime)
                    examSubmit(paperAnswer=paperAnswer)  # 提交试卷
                    examResult(paperId=paperId)  # 查看试卷结果
                    pass
                else:
                    print('查询课程试卷失败，提示信息：', result['errormsg'])
                print(course['课程名称'], '课程答卷结束。。。\n')
                pass
            pass

        elif key == 7:  # 更新直播回放信息
            image_path = input('请输入直播二维码图片地址：')
            if image_path:
                scene = getImageScene(imagePath=image_path)  # 更新房间号信息到配置文件
                channelId = getLiveChannelId(scene=scene)
            else:
                channelId = dic['直播信息']['channelId']
            updateLivePlanInfo(channelId=channelId)
            print('更新学习计划结束，请检查配置文件！')
            pass

        elif key == 8:  # 直播回放视频打卡
            punchNo = input('请输入需打卡的打卡编号(提示：配置文件.json，空回车则默认全部打卡)：')
            if punchNo:
                for punchInfo in dic['直播信息']['需打卡信息']:
                    if punchNo == punchInfo['打卡编号']:  # 没打卡成功的数据，重新打卡
                        livePunch(channelId=dic['直播信息']['channelId'], runchType=punchInfo['打卡类型'],
                                  runchNo=punchInfo['打卡编号'], recordId=int(time.time() * 1000))
                        break
            else:
                for punchInfo in dic['直播信息']['需打卡信息']:
                    if not punchInfo['是否有打卡']:  # 没打卡成功的数据，重新打卡
                        livePunch(channelId=dic['直播信息']['channelId'], runchType=punchInfo['打卡类型'],
                                  runchNo=punchInfo['打卡编号'], recordId=int(time.time() * 1000))
            print('打卡结束，可在重新更新直播信息后，查看配置文件.json')
            pass

        elif key == 9:  # 直播回放视频进度保存
            totalDuration = input('请输入要快进的秒数(默认计划秒数(非实际秒数)，如有输入数值，需大于60)：')
            if totalDuration:
                totalDuration = int(totalDuration)
            else:
                totalDuration = (datetime.fromtimestamp(dic['直播信息']['计划结束时间'] // 1000) - datetime.fromtimestamp(
                    dic['直播信息']['计划开始时间'] // 1000)).seconds

            for currentDuration in range(60, totalDuration, 60):
                recordId = int(time.time() * 1000)
                liveDurationSave(channelId=dic['直播信息']['channelId'], recordId=recordId, currentDuration=currentDuration-60)
                liveDurationSave(channelId=dic['直播信息']['channelId'], recordId=recordId, currentDuration=currentDuration)
            # 补充最后一个进度保存
            recordId = int(time.time() * 1000)
            liveDurationSave(channelId=dic['直播信息']['channelId'], recordId=recordId,
                             currentDuration=totalDuration - 60)
            liveDurationSave(channelId=dic['直播信息']['channelId'], recordId=recordId, currentDuration=totalDuration)
            pass

        elif key == 10:  # 功能测试
            print('s')
            pass
        elif key == 11:  # 结束程序
            session.close()
            print('程序运行结束')
            break
        print('\n')

        # elif key == 7:  # 查看直播回放
        #     image_path = input('请输入直播间二维码图片地址：')
        #     totalDuration = int(input('请输入要回放视频的时长（秒）：'))
        #     scene_url = get_image_url(image_path)
        #     channelId = get_livePlan_Info(scene_url)
        #
        #     interval = 30 if totalDuration // 100 > 30 else totalDuration // 100  # 模拟请求时间间隔
        #
        #     for currentDuration in range(interval, totalDuration + 1, interval):
        #         recordId = int(time.time() * 1000)  # 时间戳
        #         livePlan(channelId=channelId, recordId=recordId,
        #                  currentDuration=(currentDuration - interval))
        #         livePlan(channelId=channelId, recordId=recordId, currentDuration=currentDuration)
        #     livePlan(channelId=channelId, recordId=recordId, currentDuration=totalDuration)
        #     print('观看直播结束！')

    pass
