
# TodoList Python 세팅
```python
pip install plyer
pip install apscheduler
```
# Description
HTML, JS, Python으로 구성된 프로젝트입니다.
python webview를 통해서 HTML과 연결하도록 만들었습니다. 

# 기능 설명
일정 등록하면 일정 데이터가 tasks.json에 등록되며,
task.json을 기준으로 일정이 관리가 됩니다.

알람은 4시간 전, 2시간 전, 30분 전에 출력 됩니다.

# 함수 설명

알람 설정 함수
```python
def schedule_alarms(task, task_id) 함수에서

alert_times = [
            (deadline - timedelta(hours=4), "⏰ 4시간 전! 🚀 제목 : "),
            (deadline - timedelta(hours=2), "⏰ 2시간 전! 🚀 제목 : "),
            (deadline - timedelta(minutes=30), "⏰ 30분 전! 🚀 제목 : ")
    ]

    
#시간 : Ex) hours = 1 -> 1시간 
#분 : Ex) minutes = 30 -> 30분
#초 : Ex) seconds = 60 -> 60초

```

알람 설정 취소 함수입니다.<br>
일정 완료 표시하실 때, 
조기 완료이면 아래에 cancel_alarms 호출 추가해주시면 될 것 같습니다. <br>
task_id는 delete_task 참조 바랍니다.
```python

def cancel_alarms(task_id):
    for i in range(3):
        job_id = f"{task_id}-{i}"
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
```



