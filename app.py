import streamlit as st
import pandas as pd
import datetime

# DASS-21 question texts (official items)
question_texts = [
    "I found it hard to wind down",
    "I was aware of dryness of my mouth",
    "I couldn’t seem to experience any positive feeling at all",
    "I experienced breathing difficulty (e.g., excessively rapid breathing, breathlessness in the absence of physical exertion)",
    "I found it difficult to work up the initiative to do things",
    "I tended to over-react to situations",
    "I experienced trembling (e.g., in the hands)",
    "I felt that I was using a lot of nervous energy",
    "I was worried about situations in which I might panic and make a fool of myself",
    "I felt that I had nothing to look forward to",
    "I found myself getting agitated",
    "I found it difficult to relax",
    "I felt down-hearted and blue",
    "I was intolerant of anything that kept me from getting on with what I was doing",
    "I felt I was close to panic",
    "I was unable to become enthusiastic about anything",
    "I felt I wasn’t worth much as a person",
    "I felt that I was rather touchy",
    "I was aware of the beating of my heart in the absence of physical exertion (e.g., sense of heart rate increase, heart missing a beat)",
    "I felt scared without any good reason",
    "I felt that life was meaningless"
]

# Mapping of questions to scales
questions = {
    "Stress": [1, 6, 8, 11, 12, 14, 18],
    "Anxiety": [2, 4, 7, 9, 15, 19, 20],
    "Depression": [3, 5, 10, 13, 16, 17, 21]
}

options = {
    0: "Did not apply to me at all",
    1: "Applied to me to some degree, or some of the time",
    2: "Applied to me to a considerable degree, or a good part of the time",
    3: "Applied to me very much, or most of the time"
}

st.title("DASS-21 Online Assessment")

responses = {}
for i, q in enumerate(question_texts, start=1):
    responses[i] = st.radio(f"{i}. {q}", list(options.keys()), format_func=lambda x: options[x], index=0)

if st.button("Submit"):
    # Calculate scores
    scores = {}
    for scale, qnums in questions.items():
        total = sum(responses[q] for q in qnums) * 2
        scores[scale] = total

    # Interpretation
    severity = {
        "Depression": [(0,9,"Normal"), (10,13,"Mild"), (14,20,"Moderate"), (21,27,"Severe"), (28,100,"Extremely Severe")],
        "Anxiety": [(0,7,"Normal"), (8,9,"Mild"), (10,14,"Moderate"), (15,19,"Severe"), (20,100,"Extremely Severe")],
        "Stress": [(0,14,"Normal"), (15,18,"Mild"), (19,25,"Moderate"), (26,33,"Severe"), (34,100,"Extremely Severe")]
    }

    st.subheader("Your Results")
    for scale, value in scores.items():
        level = next(label for low, high, label in severity[scale] if low <= value <= high)
        st.write(f"**{scale}: {value} → {level}**")

    # Save responses + results
    df = pd.DataFrame([{
        "timestamp": datetime.datetime.now(),
        **responses,
        **scores
    }])
    try:
        existing = pd.read_csv("dass21_results.csv")
        df = pd.concat([existing, df], ignore_index=True)
    except FileNotFoundError:
        pass
    df.to_csv("dass21_results.csv", index=False)

    st.success("✅ Your responses have been recorded.")

