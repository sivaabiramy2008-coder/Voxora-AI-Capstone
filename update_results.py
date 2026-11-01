from pathlib import Path

p = Path("sample_outputs/final_test_results.txt")
s = p.read_text(encoding="utf-8") if p.exists() else "VOXORA AI - FINAL TEST RESULTS\n"
s += "\nPRACTICE QUESTION API TEST\n"
s += "Total questions: 52\n"
s += "HTTP 200 responses: 52\n"
s += "Evaluation type: API response availability only; answer accuracy not scored.\n"
s += "\nLIMITATIONS\n"
s += "- Gnani live voice returned INVALID_API_KEY during testing.\n"
s += "- Batch audio was not tested because no audio samples were available.\n"
p.write_text(s, encoding="utf-8")
print("Final test report updated.")
