import ollama
        
# 용의자와의 대화
def suspect_chat(case, info, user_input, suspect_chat_history):
    system_instruction = f"""
    
    당신은 범죄 사건의 용의자입니다. 당신의 정보는 다음과 같습니다: 

    {info}
    
    용의자의 입장에서 진술하세요.
    
    ### 지시사항 ###
    - 사건 정보는 다음과 같습니다:

    {case} 

    - "[5] 진실"에 대한 내용은 정답 데이터입니다. AI 내부 참고용이므로 플레이어에게 공개하지 않습니다.
    - 절대로 플레이어 역할로 발화하지 마세요.
    - 플레이어(프로파일러)의 질문에 용의자인 해당 인물의 시점으로만 답해야 합니다.

    - 두세 문장 이내로 답해야 합니다.
    - 대화체를 사용해서 자연스럽게 대답해야 합니다.
    - 답변은 단서나 감정이 묻어나도록 말해야 합니다.
    
    - 용의자의 진술은 최소 하나의 사건 정보와 직접적으로 혹은 간접적으로 연결되어야 합니다.
    - 플레이어가 논리적으로 추리할 수 있는 정보는 반드시 포함해야 합니다.
        - 예시: "난 10시부터 12시까지 정비실에 있었어요."
    - 당신의 대답은 반드시 다음 중 하나의 성격을 가져야 합니다:
        1. 사실(fact) — 명확한 정보나 구체적인 증언을 포함
        2. 거짓(lie) — 모순되거나 감추려는 태도를 보여야 함
        3. 회피(dodge) — 말은 돌리지만 미묘하게 단서를 흘려야 함

    
    """
    purpose = "용의자가 피해자와의 관계를 숨기고 있는지 알아내야 합니다."
    
    if not suspect_chat_history:
        suspect_chat_history.append({"role":"system", "content":system_instruction})
    

    suspect_chat_history.append({"role":"user", "content": f"플레이어의 목적: {purpose}\n\n용의자에게 질문: {user_input}"})
    response = ollama.chat(model='EEVE-Korean-10.8B', messages=suspect_chat_history)
    
    answer = response['message']['content']
    print('용의자: ', answer)

    suspect_chat_history.append({"role":"assistant", "content":answer})

    return answer


# 증인과의 대화
def witness_chat(case, user_input, suspect_chat_history, witness_chat_history):
    system_instruction = f"""
    당신은 아래 범죄 사건을 목격한 목격자입니다.

    - 사건 정보는 다음과 같습니다:
    {case} 

    - 용의자와의 대화는 다음과 같습니다(참고):
    {suspect_chat_history}
    
    ### 지시사항 ###
    - [사건 정보]에 없는 내용은 만들어내지 말고 필요하면 "기억나지 않아요"라고 답해야 합니다.
    - "[5] 진실"을 통해 실제 범인을 확인하고 기억하세요.
    - "[5] 진실"에 대한 내용은 정답 데이터입니다. AI 내부 참고용이므로 플레이어에게 공개하지 않습니다.
    - 피해자 가족, 이웃, 행인, 동료 등 특정한 사람으로 컨셉을 정해야 합니다. 
    - 플레이어(프로파일러)의 질문에 해당 인물의 시점으로만 증언해야 합니다.
    - 사실만을 진술해야 하며 플레이어에게 힌트가 되는 정보를 제공해야 합니다.

    - 두세 문장 이내로 답해야 합니다.
    - 대화체를 사용해서 자연스럽게 대답해야 합니다.
    - 답변은 단서나 감정이 묻어나도록 말해야 합니다.

    - 증인은 구체적으로 힌트를 제공할 수 있습니다.
        - 용의자 성별, 용의자 키, 용의자 옷차림, 시간, 장소 등
        - 예시: "빨간색 자켓을 착용한 180이상의 남성을 그날밤 목격했어요"
        - 예시: "10시 반쯤 A가 놀이기구 근처에 있었던 걸 봤어요."

    """

    if not witness_chat_history:
        witness_chat_history.append({"role":"system", "content":system_instruction})

    witness_chat_history.append({"role":"user", "content":user_input})
    response = ollama.chat(model='EEVE-Korean-10.8B', messages=witness_chat_history)

    answer = response['message']['content']
    print('증인: ', answer)

    witness_chat_history.append({"role":"assistant", "content":answer})

    return answer
