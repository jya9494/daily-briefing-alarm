from gtts import gTTS

# 나중엔 타임블럭에서 추출한 텍스트가 여기 들어갈 예정
briefing_text = """
안녕하세요, 오늘은 4월 18일입니다.
오전 10시에 회의가 있고, 오후 1시에는 점심 약속이 있습니다.
오후 3시엔 보고서 작성이 계획되어 있어요.
"""

# TTS로 변환
tts = gTTS(text=briefing_text, lang='ko')
tts.save("daily_briefing.mp3")

print("✅ mp3 파일 생성 완료!")
