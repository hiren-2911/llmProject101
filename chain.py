from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException

import os
from dotenv import load_dotenv

load_dotenv()


class Chain:
    def __init__(self):
        self.llm = ChatGroq(model='llama-3.1-70b-versatile',\
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        groq_api_key=os.getenv("groq_api_key")
        )

    def extract_jobs(self, cleaned_data):
        prompt_extract = PromptTemplate.from_template(
            """
            ###SCRAPPED TEXT FROM WEBSITE:
            {page_data}
            ###INSTRUCTION:
            The scrapped text is from the career's page of a website. your job is to extract the job posting and return them in JSON format contining following keys:
            'role', 'experience', 'skills' and 'description'. Only return the valid JSON.
            ###valid JSON (NO PREAMBLE):

            """
        )


        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke(input={'page_data': cleaned_data})

        try:
            json_parser = JsonOutputParser()
            res  = json_parser.parse(res.content)
        except OutputParserException:
            raise OutputParserException("context too big. Ubanle to parse jobs")
        return res if isinstance(res, list) else [res]
       

    def write_mail(self, job, links):
        prompt_email = PromptTemplate.from_template(
            """
            ### JOB DESCRIPTION:
            {job_description}

            ### INSTRUCTION:
            You are a business development executive at AI Labs. AI Labs is an AI & Software Consulting company dedicated to facilitating
            the seamless integration of business processes through automated tools. If the Job link is not related to software, please do not generate any email.
            Over our experience, we have empowered numerous enterprises with tailored solutions, fostering scalability, 
            process optimization, cost reduction, and heightened overall efficiency. 
            Your job is to write a cold email to the client regarding the job mentioned above describing the capability of AtliQ 
            in fulfilling their needs.
            Also add the most relevant ones from the following links to showcase AI Labs's portfolio: {link_list}
            Remember you are BDE at AI Labs. 
            Do not provide a preamble.
            ### EMAIL (NO PREAMBLE):

            """
        )
        chain_email = prompt_email | self.llm
        res = chain_email.invoke({"job_description": str(job), "link_list": links})
        return res.content

# if __name__ == "__main__":
#     print(os.getenv("groq_api_key"))