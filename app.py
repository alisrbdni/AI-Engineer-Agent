"""
app.py
"""
import time
import os
import pandas as pd
import streamlit as st
from groq import Groq
from streamlit_ace import st_ace

from self_discover import (
    REASONING_MODULES,
    select_reasoning_modules,
    adapt_reasoning_modules,
    implement_reasoning_structure,
    execute_reasoning_structure
    )

API_KEY = os.environ.get("GROQ_API_KEY")
if API_KEY is None:
    try:
        API_KEY = "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"
    except KeyError:
        # Handle the case where GROQ_API_KEY is neither in the environment variables nor in Streamlit secrets
        st.error("API key not found.")
        st.stop()

client = Groq(api_key=API_KEY)

st.set_page_config(page_title="⚡️", page_icon="⚡️", layout="wide")

st.title("⚡️")


tab2, tab1 = st.tabs([ "Agent","Text Generation"])





with tab1:
    system_prompt = st.text_input("System Prompt", "You are a friendly chatbot.")
    user_prompt = st.text_input("User Prompt", "Tell me a joke.")

    # model_list = client.models.list().data
    # model_list = [model.id for model in model_list]
    model_list = ["mixtral-8x7b-32768","llama2-70b-4096"]

    model = st.radio("Select the LLM", model_list, horizontal=True)
    
    button = st.empty()
    time_taken = st.empty()
    response = st.empty()
    

    if button.button("Generate"):
        stream = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}],
            stream=True
            )

        start_time = time.time()

        streamed_text = ""

        for chunk in stream:
            chunk_content = chunk.choices[0].delta.content
            if chunk_content is not None:
                streamed_text = streamed_text + chunk_content
                response.info(streamed_text)

        time_taken.success(f"Time taken: {round(time.time() - start_time,4)} seconds")

with tab2:
    uploaded_file = st.file_uploader("Upload CSV", type=['csv'])
    df = None
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.dataframe(df)  # Display the uploaded CSV as a table

    df_list = ["M","A","D","A","U","Board","C....","GP."]

    df_type = st.radio("Select the Type", df_list, horizontal=True)
    Upload_btn = st.button("New Upload")
    Newuser_btn = st.button("New User")
    # Newuser_btn = st.button("New User")
    # Newuser_btn = st.button("New User")
    task = st.text_area("")





    reasoning_model = st.radio("Select your LLM for this reasoning task", model_list, horizontal=True, help="mixtral is recommended for better performance, but appears to be slower")

    button = st.empty()
    step4 = st.empty()
    step3 = st.empty() 
    step2 = st.empty()
    step1 = st.empty()


    if button.button("Run"):
        
        if df is not None:
            # Convert the DataFrame to a string or a format that your model can process
            csv_data_as_string = df.to_csv(index=False)
        else:
            csv_data_as_string = "No CSV data uploaded"
        
        combined_input = f"{task}\n\n of this CSV Data:\n{csv_data_as_string}"+csv_data_as_string
        # st.markdown(combined_input, unsafe_allow_html=False)
        task = combined_input
        st.markdown(task)
        
        prompt = select_reasoning_modules(REASONING_MODULES, task)
        
        select_reasoning_modules = ""
        stream_1 = client.chat.completions.create(
            model=reasoning_model,
            messages=[{"role": "system", "content": "You are a world class expert in reasoning."},
                    {"role": "user", "content": prompt}],
            stream=True
        )
        
        for chunk in stream_1:
            chunk_content = chunk.choices[0].delta.content
            if chunk_content is not None:
                select_reasoning_modules = select_reasoning_modules + chunk_content
                step1.info("Step 1: SELECT relevant reasoning modules for the task \n \n"+select_reasoning_modules)
        

        prompt = adapt_reasoning_modules(select_reasoning_modules, task)
        st.markdown(task)

        stream_2 = client.chat.completions.create(
            model=reasoning_model,
            messages=[{"role": "system", "content": "You are a world class expert in reasoning."},
                    {"role": "user", "content": prompt}],
            stream=True
        )

        adapted_modules = ""
        for chunk in stream_2:
            chunk_content = chunk.choices[0].delta.content
            if chunk_content is not None:
                adapted_modules = adapted_modules + chunk_content
                step2.info("Step 2: ADAPT the selected reasoning modules to be more specific to the task. \n \n " + adapted_modules)

        prompt = implement_reasoning_structure(adapted_modules, task)
        stream_3 = client.chat.completions.create(
            model=reasoning_model,
            messages=[{"role": "system", "content": "You are a world class expert in reasoning."},
                    {"role": "user", "content": prompt}],
            stream=True
        )

        reasoning_structure = ""
        for chunk in stream_3:
            chunk_content = chunk.choices[0].delta.content
            if chunk_content is not None:
                reasoning_structure = reasoning_structure + chunk_content
                step3.info("Step 3: IMPLEMENT the adapted reasoning modules into an actionable reasoning structure. \n \n " + reasoning_structure)

        prompt = execute_reasoning_structure(reasoning_structure, task)
        stream_4 = client.chat.completions.create(
            model=reasoning_model,
            messages=[{"role": "system", "content": "You are a world class expert in reasoning."},
                    {"role": "user", "content": prompt}],
            stream=True
        )

        
        result = ""

        for chunk in stream_4:
            chunk_content = chunk.choices[0].delta.content
            if chunk_content is not None:
                result = result + chunk_content
                step4.info("Step 4: Execute the reasoning structure to solve a specific task instance. \n \n " + result)
    code = st_ace(
            value=result,
            language='python', 
            theme='tomorrow_night',
            tab_size= 4,
            font_size=16, height=200
        )
        
        
    html = f"""
        <html>
          <head>
            <link rel="stylesheet" href="https://pyscript.net/latest/pyscript.css" />
            <script defer src="https://pyscript.net/latest/pyscript.js"></script>
          </head>
          <body>
            <py-script>{code}</py-script>
          </body>
        </html>
        """
            
    st.components.v1.html(html, height=200, scrolling=True)
                    



# ##################
# What is your task?",value="""
# you are a security engineer that is able to prioritise the most important findings that need to be fixed. Some aspects you may want to consider
#     - If a finding is in a test file or something that looks like a test it should not be as high of a priority
#     - How exploitable is the finding. Most static analysis tools will not tell you how exploitable a finding is because they do not have enough context of the repo. Can you fix this and incorporate exploitability in your analysis. Ensure you can reproduce reliable and consistent results.
#     - How much engineering effort will it take to fix the finding. Some fixes are simple one line fixes that only take a couple of minutes. Other vulnerabilities require you to restructure your program that could be expensive. Calculate how long it will take to fix findings. You should also provide a justification which can be relayed to the end user.
# - Once findings have been prioritised your next task is to incorporate the most important findings into the current sprint.
#     - Analyse the engineering time taken to fix the finding and see if it fits into the sprint
#     - Ensure that findings are allocated to the correct team and members

# Remember you should build an agent for the following tasks. It should first prioritise findings then understand the sprint play to ensure associated tickets. Document your approach to solving the problem.
# {
# 	"Golang errors": {},
# 	"Issues": [
# 		{
# 			"severity": "MEDIUM",
# 			"confidence": "MEDIUM",
# 			"cwe": {
# 				"id": "88",
# 				"url": "https://cwe.mitre.org/data/definitions/88.html"
# 			},
# 			"rule_id": "G107",
# 			"details": "Potential HTTP request made with variable url",
# 			"file": "/home/rahul/code/nullify/Rebel-Alliance/the-force/data/expected-comments/golang/main.go",
# 			"code": "11: 	url := fmt.Sprintf("http://%s/", host)
# 12: 	res, err := http.Get(url)
# 13: 	if err != nil {
# ",
# 			"line": "12",
# 			"column": "14",
# 			"nosec": false,
# 			"suppressions": null
# 		},
# 		{
# 			"severity": "MEDIUM",
# 			"confidence": "HIGH",
# 			"cwe": {
# 				"id": "703",
# 				"url": "https://cwe.mitre.org/data/definitions/703.html"
# 			},
# 			"rule_id": "G307",
# 			"details": "Deferring unsafe method "Close" on type "*os.File"",
# 			"file": "/home/rahul/code/nullify/Rebel-Alliance/the-force/data/expected-comments/golang/test/main.go",
# 			"code": "13: 
# 14: 	defer file.Close()
# 15: 
# ",
# 			"line": "14",
# 			"column": "2",
# 			"nosec": false,
# 			"suppressions": null
# 		},
# 		{
# 			"severity": "LOW",
# 			"confidence": "HIGH",
# 			"cwe": {
# 				"id": "242",
# 				"url": "https://cwe.mitre.org/data/definitions/242.html"
# 			},
# 			"rule_id": "G103",
# 			"details": "Use of unsafe calls should be audited",
# 			"file": "/home/rahul/code/nullify/Rebel-Alliance/the-force/data/expected-comments/golang/go-unsafepointer-poc/struct-cast/main.go",
# 			"code": "26: 
# 27: 	violet := *(*VioletStruct)(unsafe.Pointer(&pink))
# 28: 
# ",
# 			"line": "27",
# 			"column": "29",
# 			"nosec": false,
# 			"suppressions": null
# 		},
# 		{
# 			"severity": "LOW",
# 			"confidence": "HIGH",
# 			"cwe": {
# 				"id": "242",
# 				"url": "https://cwe.mitre.org/data/definitions/242.html"
# 			},
# 			"rule_id": "G103",
# 			"details": "Use of unsafe calls should be audited",
# 			"file": "/home/rahul/code/nullify/Rebel-Alliance/the-force/data/expected-comments/golang/go-unsafepointer-poc/race-slice/main.go",
# 			"code": "28: 
# 29: 	return *(*[]byte)(unsafe.Pointer(sliceHeader))
# 30: }
# ",
# 			"line": "29",
# 			"column": "20",
# 			"nosec": false,
# 			"suppressions": null
# 		},
# 		{
# 			"severity": "LOW",
# 			"confidence": "HIGH",
# 			"cwe": {
# 				"id": "242",
# 				"url": "https://cwe.mitre.org/data/definitions/242.html"
# 			},
# 			"rule_id": "G103",
# 			"details": "Use of unsafe calls should be audited",
# 			"file": "/home/rahul/code/nullify/Rebel-Alliance/the-force/data/expected-comments/golang/go-unsafepointer-poc/race-slice/main.go",
# 			"code": "18: func unsafeStringToBytes(s *string) []byte {
# 19: 	sh := (*reflect.StringHeader)(unsafe.Pointer(s))
# 20: 	sliceHeader := &reflect.SliceHeader{
# ",
# 			"line": "19",
# 			"column": "32",
# 			"nosec": false,
# 			"suppressions": null
# 		},
# 		{
# 			"severity": "LOW",
# 			"confidence": "HIGH",
# 			"cwe": {
# 				"id": "242",
# 				"url": "https://cwe.mitre.org/data/definitions/242.html"
# 			},
# 			"rule_id": "G103",
# 			"details": "Use of unsafe calls should be audited",
# 			"file": "/home/rahul/code/nullify/Rebel-Alliance/the-force/data/expected-comments/golang/go-unsafepointer-poc/information-leak/main.go",
# 			"code": "13: 	// read from memory behind buffer
# 14: 	var leakingInformation = (*[8+17]byte)(unsafe.Pointer(&harmlessData[0]))
# 15: 
# ",
# 			"line": "14",
# 			"column": "41",
# 			"nosec": false,
# 			"suppressions": null
# 		},
# 		{
# 			"severity": "LOW",
# 			"confidence": "HIGH",
# 			"cwe": {
# 				"id": "242",
# 				"url": "https://cwe.mitre.org/data/definitions/242.html"
# 			},
# 			"rule_id": "G103",
# 			"details": "Use of unsafe calls should be audited",
# 			"file": "/home/rahul/code/nullify/Rebel-Alliance/the-force/data/expected-comments/golang/go-unsafepointer-poc/go-fuse/opcode.go",
# 			"code": "24: 
# 25: 	forgets := *(*[]_ForgetOne)(unsafe.Pointer(h))
# 26: 	for i, f := range forgets {
# ",
# 			"line": "25",
# 			"column": "30",
# 			"nosec": false,
# 			"suppressions": null
# 		},
# 		{
# 			"severity": "LOW",
# 			"confidence": "HIGH",
# 			"cwe": {
# 				"id": "242",
# 				"url": "https://cwe.mitre.org/data/definitions/242.html"
# 			},
# 			"rule_id": "G103",
# 			"details": "Use of unsafe calls should be audited",
# 			"file": "/home/rahul/code/nullify/Rebel-Alliance/the-force/data/expected-comments/golang/go-unsafepointer-poc/go-fuse/opcode.go",
# 			"code": "19: 	h := &reflect.SliceHeader{
# 20: 		Data: uintptr(unsafe.Pointer(&req.arg[0])),
# 21: 		Len:  int(in.Count),
# ",
# 			"line": "20",
# 			"column": "17",
# 			"nosec": false,
# 			"suppressions": null
# 		},
# 		{
# 			"severity": "LOW",
# 			"confidence": "HIGH",
# 			"cwe": {
# 				"id": "242",
# 				"url": "https://cwe.mitre.org/data/definitions/242.html"
# 			},
# 			"rule_id": "G103",
# 			"details": "Use of unsafe calls should be audited",
# 			"file": "/home/rahul/code/nullify/Rebel-Alliance/the-force/data/expected-comments/golang/go-unsafepointer-poc/go-fuse/opcode.go",
# 			"code": "11: 	in := (*_BatchForgetIn)(req.inData)
# 12: 	wantBytes := uintptr(in.Count) * unsafe.Sizeof(_ForgetOne{})
# 13: 	if uintptr(len(req.arg)) < wantBytes {
# ",
# 			"line": "12",
# 			"column": "35",
# 			"nosec": false,
# 			"suppressions": null
# 		},
# 		{
# 			"severity": "LOW",
# 			"confidence": "HIGH",
# 			"cwe": {
# 				"id": "242",
# 				"url": "https://cwe.mitre.org/data/definitions/242.html"
# 			},
# 			"rule_id": "G103",
# 			"details": "Use of unsafe calls should be audited",
# 			"file": "/home/rahul/code/nullify/Rebel-Alliance/the-force/data/expected-comments/golang/go-unsafepointer-poc/go-fuse/exploit.go",
# 			"code": "28: 		inHeader:            nil,
# 29: 		inData:              unsafe.Pointer(&_BatchForgetIn{Count: 5,}),
# 30: 		arg:                 forgetObjectBytes,
# ",
# 			"line": "29",
# 			"column": "24",
# 			"nosec": false,
# 			"suppressions": null
# 		},
# 		{
# 			"severity": "LOW",
# 			"confidence": "HIGH",
# 			"cwe": {
# 				"id": "242",
# 				"url": "https://cwe.mitre.org/data/definitions/242.html"
# 			},
# 			"rule_id": "G103",
# 			"details": "Use of unsafe calls should be audited",
# 			"file": "/home/rahul/code/nullify/Rebel-Alliance/the-force/data/expected-comments/golang/go-unsafepointer-poc/go-fuse/exploit.go",
# 			"code": "18: 	sH.Len *= 16
# 19: 	forgetObjectBytes := *(*[]byte)(unsafe.Pointer(sH))
# 20: 
# ",
# 			"line": "19",
# 			"column": "34",
# 			"nosec": false,
# 			"suppressions": null
# 		},
# 		{
# 			"severity": "LOW",
# 			"confidence": "HIGH",
# 			"cwe": {
# 				"id": "242",
# 				"url": "https://cwe.mitre.org/data/definitions/242.html"
# 			},
# 			"rule_id": "G103",
# 			"details": "Use of unsafe calls should be audited",
# 			"file": "/home/rahul/code/nullify/Rebel-Alliance/the-force/data/expected-comments/golang/go-unsafepointer-poc/go-fuse/exploit.go",
# 			"code": "15: 
# 16: 	sH := (*reflect.SliceHeader)(unsafe.Pointer(&forgetObjects))
# 17: 	sH.Cap *= 16
# ",
# 			"line": "16",
# 			"column": "31",
# 			"nosec": false,
# 			"suppressions": null
# 		},
# 		{
# 			"severity": "LOW",
# 			"confidence": "HIGH",
# 			"cwe": {
# 				"id": "242",
# 				"url": "https://cwe.mitre.org/data/definitions/242.html"
# 			},
# 			"rule_id": "G103",
# 			"details": "Use of unsafe calls should be audited",
# 			"file": "/home/rahul/code/nullify/Rebel-Alliance/the-force/data/expected-comments/golang/go-unsafepointer-poc/escape-analysis/main.go",
# 			"code": "19: 	}
# 20: 	return *(*string)(unsafe.Pointer(&strHeader))
# 21: }
# ",
# 			"line": "20",
# 			"column": "20",
# 			"nosec": false,
# 			"suppressions": null
# 		},
# 		{
# 			"severity": "LOW",
# 			"confidence": "HIGH",
# 			"cwe": {
# 				"id": "242",
# 				"url": "https://cwe.mitre.org/data/definitions/242.html"
# 			},
# 			"rule_id": "G103",
# 			"details": "Use of unsafe calls should be audited",
# 			"file": "/home/rahul/code/nullify/Rebel-Alliance/the-force/data/expected-comments/golang/go-unsafepointer-poc/escape-analysis/main.go",
# 			"code": "14: func BytesToString(b []byte) string {
# 15: 	bytesHeader := (*reflect.SliceHeader)(unsafe.Pointer(&b))
# 16: 	strHeader := reflect.StringHeader{
# ",
# 			"line": "15",
# 			"column": "40",
# 			"nosec": false,
# 			"suppressions": null
# 		},
# 		{
# 			"severity": "LOW",
# 			"confidence": "HIGH",
# 			"cwe": {
# 				"id": "242",
# 				"url": "https://cwe.mitre.org/data/definitions/242.html"
# 			},
# 			"rule_id": "G103",
# 			"details": "Use of unsafe calls should be audited",
# 			"file": "/home/rahul/code/nullify/Rebel-Alliance/the-force/data/expected-comments/golang/go-unsafepointer-poc/code-injection/main.go",
# 			"code": "21: 	sliceHeader := (*reflect.SliceHeader)(unsafe.Pointer(&confusedSlice))
# 22: 	harmlessDataAddress := uintptr(unsafe.Pointer(&(harmlessData[0])))
# 23: 	sliceHeader.Data = harmlessDataAddress
# ",
# 			"line": "22",
# 			"column": "33",
# 			"nosec": false,
# 			"suppressions": null
# 		},
# 		{
# 			"severity": "LOW",
# 			"confidence": "HIGH",
# 			"cwe": {
# 				"id": "242",
# 				"url": "https://cwe.mitre.org/data/definitions/242.html"
# 			},
# 			"rule_id": "G103",
# 			"details": "Use of unsafe calls should be audited",
# 			"file": "/home/rahul/code/nullify/Rebel-Alliance/the-force/data/expected-comments/golang/go-unsafepointer-poc/code-injection/main.go",
# 			"code": "20: 	confusedSlice := make([]byte, 512)
# 21: 	sliceHeader := (*reflect.SliceHeader)(unsafe.Pointer(&confusedSlice))
# 22: 	harmlessDataAddress := uintptr(unsafe.Pointer(&(harmlessData[0])))
# ",
# 			"line": "21",
# 			"column": "40",
# 			"nosec": false,
# 			"suppressions": null
# 		},
# 		{
# 			"severity": "LOW",
# 			"confidence": "HIGH",
# 			"cwe": {
# 				"id": "242",
# 				"url": "https://cwe.mitre.org/data/definitions/242.html"
# 			},
# 			"rule_id": "G103",
# 			"details": "Use of unsafe calls should be audited",
# 			"file": "/home/rahul/code/nullify/Rebel-Alliance/the-force/data/expected-comments/golang/go-unsafepointer-poc/code-flow-redirection/main.go",
# 			"code": "53: 
# 54: 	arrayCopy((*[64]byte)(unsafe.Pointer(&theData.harmlessData)), &theData.exploit)
# 55: }
# ",
# 			"line": "54",
# 			"column": "24",
# 			"nosec": false,
# 			"suppressions": null
# 		}
# 	],
# 	"Stats": {
# 		"files": 11,
# 		"lines": 493,
# 		"nosec": 0,
# 		"found": 17
# 	},
# 	"GosecVersion": "dev"
# }
# Example Code Sprint
# To-do
# In progress
# Complete
# package main

# import (
# 	"fmt"
# 	"net/http"
# 	"os"
# )

# func main() {
# 	host := os.Args[0]
# 	url := fmt.Sprintf("http://%s/", host)
# 	res, err := http.Get(url)
# 	if err != nil {
# 		panic(err)
# 	}
# 	fmt.Printf("Status: %d", res.StatusCode)
# }


# come up with sprint planing of your findings in this code and create tickets and assign them based on sprint and availability of team and write code fixes on ticket and write final tickets in sprints with heading and code samples and priority and assignees

# #######
