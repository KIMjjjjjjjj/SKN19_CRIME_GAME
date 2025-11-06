# - 사건 소개 페이지: 사건 선택 | 사건 파일 및 신문 스크랩 확인
# - 증거물 페이지: 증거물 정보 및 이미지 확인
# - 심문 페이지: 용의자/증인과의 대화 | 대화를 통해 얻은 정보 요약
# - 엔딩 페이지: 용의자 지목 후 결과 확인 
import streamlit as st
import time
import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.eeve_chat import suspect_chat, witness_chat

# 페이지 설정
st.set_page_config(page_title="〈The Room of Lies〉", page_icon="🕵️‍♀️", layout="wide")


# 세션 스테이트 초기화
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'intro'
if 'selected_case' not in st.session_state:
    st.session_state.selected_case = None
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = {}
if 'opportunity' not in st.session_state:
    st.session_state.opportunity = 2
if 'game_over' not in st.session_state:
    st.session_state.game_over = False
if 'game_result' not in st.session_state:
    st.session_state.game_result = None
if 'cases_data' not in st.session_state:
    st.session_state.cases_data = {}
if 'suspect_chat_history' not in st.session_state:
    st.session_state.suspect_chat_history = {}
if "witness_chat_history" not in st.session_state:
    st.session_state.witness_chat_history = []

# JSON 파일 로드 함수
def load_case_files():
    cases = {}
    for i in range(1, 6):
        file_path = f'./../data/case_file{i}.json'
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                case_data = json.load(f)
                # 사건명 추출
                case_name = case_data.get('사건 개요', [{}])[0].get('사건명', f'사건 #{i}')
                cases[case_name] = case_data
        except FileNotFoundError:
            st.warning(f'{file_path} 파일을 찾을 수 없습니다.')
        except json.JSONDecodeError:
            st.error(f'{file_path} 파일을 읽는 중 오류가 발생했습니다.')
        except Exception as e:
            st.error(f'{file_path} 로드 중 오류: {str(e)}')
    
    return cases

# 사건 데이터 로드
if not st.session_state.cases_data:
    st.session_state.cases_data = load_case_files()

CASES = st.session_state.cases_data

# 용의자 정보 추출 함수
def get_suspect_info(case, suspect_name):
    # 용의자 정보 문자열 반환
    suspects = case.get('용의자', [])
    for suspect in suspects:
        personal_info = suspect.get('개인 정보', {})
        if personal_info.get('이름') == suspect_name:
            info = f"""
            이름: {personal_info.get('이름')}
            나이: {personal_info.get('나이')}
            성별: {personal_info.get('성별')}
            직업: {personal_info.get('직업')}
            신체: 키 {suspect.get('신체 정보', {}).get('키')}, 몸무게 {suspect.get('신체 정보', {}).get('몸무게')}
            피해자와의 관계: {suspect.get('관계')}
            알리바이: {suspect.get('알리바이')}
            의심점: {suspect.get('의심점')}
            """
            return info.strip()
    return "정보 없음"

    
# 배경 이미지 함수
def set_background():
    # 배경 이미지 설정
    st.markdown("""
        <style>
        /* 전체 배경 설정 */
        .stApp {
            background: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)),
                        url("https://www.shutterstock.com/image-vector/frame-crime-investigation-elements-caution-600nw-2452782777.jpg");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }
        
        /* 사이드바 배경 */
        [data-testid="stSidebar"] {
            background: rgba(20, 20, 30, 0.95);
        }
        
        /* 메인 콘텐츠 영역 투명도 조정 */
        .main .block-container {
            background: rgba(255, 255, 255, 0.95);
            padding: 2rem;
            border-radius: 10px;
        }
        </style>
        """, unsafe_allow_html=True
    )

    # CSS 스타일
    st.markdown("""
        <style>
        .big-font {
            font-size:30px !important;
            font-weight: bold;
        }
        .evidence-box {
            padding: 20px;
            border-radius: 10px;
            background-color: #f0f2f6;
            margin: 10px 0;
        }
        .suspect-box {
            padding: 15px;
            border-radius: 8px;
            background-color: #e8eaf6;
            margin: 10px 0;
        }
        </style>
        """, unsafe_allow_html=True
    )


# 사이드바 네비게이션 함수
def sidebar_navigation():
    with st.sidebar:
        st.title("〈The Room of Lies〉")
        st.divider()
        
        if st.button("🗄️사건 파일", use_container_width=True):
            st.session_state.current_page = 'intro'
        
        if st.session_state.selected_case:
            if st.button("🔬 증거물", use_container_width=True):
                st.session_state.current_page = 'evidence'
            
            if st.button("🕵️‍♀️ 용의자 심문", use_container_width=True):
                st.session_state.current_page = 'interrogation'

            if st.button("👩‍💻 목격자 진술", use_container_width=True):
                st.session_state.current_page = 'witness'
            
            if st.button("⛔ 엔딩", use_container_width=True):
                st.session_state.current_page = 'ending'

        st.divider()
        if st.session_state.selected_case and not st.session_state.game_over:
            st.metric("남은 기회", f"{st.session_state.opportunity}/2", 
                    delta=None if st.session_state.opportunity == 2 else f"-{2-st.session_state.opportunity}")
            

# 사건 소개 페이지
def main():
    st.title("🗄️사건 파일")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("사건 선택")
        
        case_list = list(CASES.keys()) 
        selected = st.selectbox(
            "수사할 사건을 선택하세요.",
            options=case_list,
            key="case_selectbox" 
        )

        if st.button("수사 시작", type="primary"):
            st.session_state.selected_case = selected
            st.session_state.opportunity = 2
            st.session_state.game_over = False
            st.session_state.game_result = None
            st.session_state.conversation_history = {}
            st.session_state.suspect_chat_history = {}
            st.session_state.witness_chat_history = []
            st.rerun()
    
    with col2:
        if st.session_state.selected_case and st.session_state.selected_case in CASES:
            case = CASES[st.session_state.selected_case]
            case_overview = case.get("사건 개요", [{}])[0]
            
            st.subheader(case_overview.get("사건명", "사건명 없음"))
            
            # 사건 정보 표시
            st.write(f"**범행 시간:** {case_overview.get('범행 시간', '알 수 없음')}")
            st.write(f"**범행 장소:** {case_overview.get('범행 장소', '알 수 없음')}")
            st.write(f"**범행 유형:** {case_overview.get('범행 유형', '알 수 없음')}")
            
            # 피해자 정보
            victim = case_overview.get('피해자', {})
            victim_info = victim.get('개인 정보', {})
            st.write(f"**피해자:** {victim_info.get('이름', '알 수 없음')} ({victim_info.get('나이', '?')}세, {victim_info.get('직업', '알 수 없음')})")
            
            st.divider()
            
            # 신문 기사
            st.subheader("신문 기사")
            articles = case.get("신문 기사", [])
            if articles:
                for article in articles:
                    st.info(f"**{article.get('기사 제목', '제목 없음')}**\n\n{article.get('기사 내용', '내용 없음')}")
            else:
                st.write("신문 기사가 없습니다.")

# 증거물 페이지
def evidence_page():
    st.title("🔬 증거물 분석")
    case = CASES[st.session_state.selected_case]
    
    evidence_list = case.get("증거물", [])
    if not evidence_list:
        st.info("증거물 정보가 없습니다.")
        return
    
    # 증거물 아이콘 매핑
    evidence_icons = {
        "신분증": "🪪",
        "혈흔": "🩸",
        "CCVT": "📹",
        "영상": "📹",
        "안전바": "🎢",
        "기본": "🔍"
    }
    
    cols = st.columns(3)
    for idx, evidence in enumerate(evidence_list):
        with cols[idx % 3]:
            st.markdown(f"<div class='evidence-box'>", unsafe_allow_html=True)
            
            # 증거명에 따라 아이콘 선택
            evidence_name = evidence.get("증거명", "증거")
            icon = "🔍"
            for key, val in evidence_icons.items():
                if key in evidence_name:
                    icon = val
                    break
            
            st.markdown(f"<div style='font-size: 60px; text-align: center;'>{icon}</div>", unsafe_allow_html=True)
            st.markdown(f'#### {evidence_name}')
            st.write(f"**발견 위치:** {evidence.get('발견 위치', '알 수 없음')}")
            st.write(f"**설명:** {evidence.get('설명', '설명 없음')}")
            st.markdown("</div>", unsafe_allow_html=True)

# 심문 페이지
def interrogation_page():
    st.title("🕵️‍♀️ 용의자 심문")
    
    case = CASES[st.session_state.selected_case]
    suspects = case.get("용의자", [])
    
    # 용의자 이름 목록 생성
    suspect_names = [s.get('개인 정보', {}).get('이름', f'용의자 {i+1}') for i, s in enumerate(suspects)]
    
    # 용의자 선택
    suspect_name = st.selectbox("심문할 용의자를 선택하세요.", suspect_names)
    
    # 선택된 용의자 정보 가져오기
    selected_suspect = None
    for suspect in suspects:
        if suspect.get('개인 정보', {}).get('이름') == suspect_name:
            selected_suspect = suspect
            break

    # 대화 이력 표시
    chat_key = f"{st.session_state.selected_case}_{suspect_name}"
    
    col1, col2 = st.columns([1, 2])
    with col1:
        personal_info = selected_suspect.get('개인 정보', {})
        body_info = selected_suspect.get('신체 정보', {})
        
        st.subheader(personal_info.get('이름', '이름 없음'))
        st.write(f"**나이:** {personal_info.get('나이', '?')}세")
        st.write(f"**성별:** {personal_info.get('성별', '알 수 없음')}")
        st.write(f"**직업:** {personal_info.get('직업', '알 수 없음')}")
        st.write(f"**신체:** {body_info.get('키', '?')}, {body_info.get('몸무게', '?')}")
        
        st.divider()
        st.write(f"**피해자와의 관계:**")
        st.caption(selected_suspect.get('관계', '알 수 없음'))
        
        st.write(f"**알리바이:**")
        st.caption(selected_suspect.get('알리바이', '알 수 없음'))
        
        st.write(f"**의심점:**")
        st.caption(selected_suspect.get('의심점', '없음'))
    
    with col2:
        st.subheader("용의자 심문")
        
        if chat_key not in st.session_state.conversation_history:
            st.session_state.conversation_history[chat_key] = []
        
        # 대화 내용 표시 (시스템 메시지 제외)
        if suspect_name in st.session_state.suspect_chat_history:
            for msg in st.session_state.suspect_chat_history[suspect_name]:
                if msg['role'] == 'user':
                    # "용의자에게 질문:" 이후 텍스트만 추출
                    content = msg['content']
                    if '용의자에게 질문:' in content:
                        question = content.split('용의자에게 질문:')[-1].strip()
                    else:
                        question = content
                    with st.chat_message("user", avatar="🕵️"):
                        st.write(question)
                elif msg['role'] == 'assistant':
                    with st.chat_message("assistant", avatar="👤"):
                        st.write(msg['content'])
        
        # 질문 입력
        user_question = st.text_input("질문을 입력하세요.", placeholder="예: 사건 당일 무엇을 하고 있었나요?", key=f"question_{suspect_name}")
        
        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            if st.button("질문하기", type="primary", use_container_width=True):
                if user_question.strip():
                    with st.spinner("용의자가 답변 중..."):
                        suspect_chat_history = st.session_state.get("suspect_chat_history", {})

                        if suspect_name not in suspect_chat_history:
                            suspect_chat_history[suspect_name] = []
                        
                        suspect_info = get_suspect_info(case, suspect_name)

                        answer = suspect_chat(case, suspect_info, user_question, suspect_chat_history[suspect_name])
                        
                        st.session_state.suspect_chat_history = suspect_chat_history

                        st.session_state.conversation_history[chat_key].append({
                            "질문": user_question,
                            "답변": answer
                        })
                        st.rerun()
                else:
                    st.warning("질문을 입력해주세요.")
        
        with col_btn2:
            if st.button("대화 초기화", use_container_width=True):
                if suspect_name in st.session_state.suspect_chat_history:
                    del st.session_state.suspect_chat_history[suspect_name]
                if chat_key in st.session_state.conversation_history:
                    del st.session_state.conversation_history[chat_key]
                st.rerun()
    
    # 대화 요약
    if chat_key in st.session_state.conversation_history and st.session_state.conversation_history[chat_key]:
        st.divider()
        st.subheader("대화 요약")
        
        for idx, conv in enumerate(st.session_state.conversation_history[chat_key], 1):
            with st.expander(f"질문 {idx}: {conv['질문'][:50]}..."):
                st.write(f"**질문:** {conv['질문']}")
                st.write(f"**답변:** {conv['답변']}")

# 증인 페이지
def witness_page():
    st.title("👩‍💻 목격자 진술")

    case = CASES[st.session_state.selected_case]
    
    # witness_chat_history 초기화
    if "witness_chat_history" not in st.session_state:
        st.session_state.witness_chat_history = []
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("용의자와의 대화 요약")
        if "conversation_history" in st.session_state and st.session_state.conversation_history:
            has_conversation = False
            for key, conv in st.session_state.conversation_history.items():
                if conv and not key.endswith('_witness'):
                    has_conversation = True
                    suspect_name = key.split('_')[-1]
                    with st.expander(f"{suspect_name}와의 대화"):
                        for qa in conv[-3:]:  # 최근 3개만 표시
                            st.caption(f"Q: {qa['질문'][:50]}...")
                            st.caption(f"A: {qa['답변'][:50]}...")
            
            if not has_conversation:
                st.caption("아직 용의자와 대화한 내역이 없습니다.")
        else:
            st.caption("아직 용의자와 대화한 내역이 없습니다.")
    
    with col2:
        st.subheader("목격자 심문")
        
        st.caption("💡 목격자는 사건의 진실을 알고 있습니다. 용의자와의 대화를 참고하여 구체적으로 질문하세요.")
        
        # 대화 내용 표시
        for msg in st.session_state.witness_chat_history:
            if msg['role'] == 'user':
                content = msg['content']
                if '목격자에게 질문:' in content:
                    question = content.split('목격자에게 질문:')[-1].strip()
                else:
                    question = content
                with st.chat_message("user", avatar="🕵️"):
                    st.write(question)
            elif msg['role'] == 'assistant':
                with st.chat_message("assistant", avatar="👤"):
                    st.write(msg['content'])
        
        st.divider()
        
        # 질문 입력
        user_question = st.text_input("질문을 입력하세요.", placeholder="예: 사건 당일 무엇을 목격했나요?", key="witness_question")
        
        col_btn1, col_btn2 = st.columns([1, 1])
        
        with col_btn1:
            if st.button("질문하기", type="primary", use_container_width=True):
                if user_question.strip():
                    with st.spinner("목격자가 답변 중..."):
                        # 증인과 대화
                        answer = witness_chat(case, user_question, st.session_state.suspect_chat_history, st.session_state.witness_chat_history)
                        st.rerun()
                else:
                    st.warning("질문을 입력해주세요.")
        
        with col_btn2:
            # 대화 초기화 버튼
            if st.button("대화 초기화", use_container_width=True):
                st.session_state.witness_chat_history = []
                st.success("대화가 초기화되었습니다.")
                time.sleep(1)
                st.rerun()
    
    # 대화 요약
    if st.session_state.witness_chat_history and len(st.session_state.witness_chat_history) > 1:
        st.divider()
        st.subheader("심문 기록")
        
        # 대화 내용 정리
        conversations = []
        for i in range(1, len(st.session_state.witness_chat_history)):
            msg = st.session_state.witness_chat_history[i]
            if msg['role'] == 'user':
                question = msg['content']
                if '목격자에게 질문:' in question:
                    question = question.split('목격자에게 질문:')[-1].strip()
                # 다음 메시지가 답변인지 확인
                if i + 1 < len(st.session_state.witness_chat_history):
                    next_msg = st.session_state.witness_chat_history[i + 1]
                    if next_msg['role'] == 'assistant':
                        conversations.append({
                            "질문": question,
                            "답변": next_msg['content']
                        })
        
        # 대화 내용 표시
        for idx, conv in enumerate(conversations, 1):
            with st.expander(f"질문 {idx}: {conv['질문'][:50]}..."):
                st.write(f"**질문:** {conv['질문']}")
                st.write(f"**답변:** {conv['답변']}")
        
        # 다운로드 버튼
        if conversations:
            export_text = "=== 목격자 심문 기록 ===\n\n"
            for idx, conv in enumerate(conversations, 1):
                export_text += f"[질문 {idx}]\n{conv['질문']}\n\n[답변 {idx}]\n{conv['답변']}\n\n"
            
            st.download_button(
                label="📥 심문 기록 다운로드",
                data=export_text,
                file_name=f"목격자_심문_기록_{st.session_state.selected_case}.txt",
                mime="text/plain"
            )


# 엔딩 페이지
def ending_page():
    st.title("⛔ 범인 지목")
    case = CASES[st.session_state.selected_case]
    
    if st.session_state.game_over:
        if st.session_state.game_result == "success":
            st.error('게임 클리어! 범인을 밝혀냈습니다!')
            st.balloons()
        else:
            st.error("게임 오버! 기회를 모두 잃어 게임이 종료됩니다.")          
        
        st.divider()
        st.subheader("사건의 진실")
        truth_list = case.get('진실', [])
        if truth_list:
            for truth in truth_list:
                st.write(f"**진짜 범인:** {truth.get('진짜 범인', '알 수 없음')}")
                st.write(f"**결정적 증거:** {truth.get('결정적 증거', '없음')}")
        
        if st.button("새 게임 시작", type="primary"):
            st.session_state.current_page = 'intro'
            st.session_state.selected_case = None
            st.session_state.opportunity = 2
            st.session_state.game_over = False
            st.session_state.game_result = None
            st.session_state.conversation_history = {}
            st.session_state.suspect_chat_history = {}
            st.session_state.witness_chat_history = []
            st.rerun()
    
    else:
        if st.session_state.opportunity == 2:
            st.info(f"수사를 마치고 범인을 지목하세요.")
        else:
            st.warning(f"무고한 사람을 지목하여 기회가 감소했습니다. 다시 추리해보세요.")
        
        # 용의자 목록 생성
        suspects = case.get("용의자", [])
        suspect_names = [s.get('개인 정보', {}).get('이름', f'용의자 {i+1}') for i, s in enumerate(suspects)]
        
        col1, col2 = st.columns([2, 1])
        with col1:
            suspect_choice = st.selectbox(
                "범인으로 지목할 용의자",
                suspect_names
            )
        
        with col2:
            st.write("")
            st.write("")
            if st.button("범인 지목", type="primary", use_container_width=True):
                truth_list = case.get('진실', [])
                if truth_list:
                    criminal = truth_list[0].get('진짜 범인', '')
                    
                    if criminal == suspect_choice:
                        st.session_state.game_over = True
                        st.session_state.game_result = "success"
                        st.rerun()
                    else:
                        st.session_state.opportunity -= 1
                        if st.session_state.opportunity == 0:
                            st.session_state.game_over = True
                            st.session_state.game_result = "failure"
                            st.rerun()
                        else:
                            st.error(f"기회가 {st.session_state.opportunity}번 남았습니다.")
                            time.sleep(2)
                            st.rerun()


# 페이지 라우팅
set_background()
sidebar_navigation()
if st.session_state.current_page == 'intro':
    main()
elif st.session_state.current_page == 'evidence':
    evidence_page()
elif st.session_state.current_page == 'interrogation':
    interrogation_page()
elif st.session_state.current_page == 'witness':
    witness_page()
elif st.session_state.current_page == 'ending':
    ending_page()

# if __name__ == '__main__':
#    main()