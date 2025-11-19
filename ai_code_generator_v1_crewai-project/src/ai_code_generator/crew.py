import os

from crewai import LLM
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from ai_code_generator.tools.code_analysis_tool import CodeAnalysisTool




@CrewBase
class AiCodeGeneratorCrew:
    """AiCodeGenerator crew"""

    
    @agent
    def senior_software_developer_and_code_generator(self) -> Agent:
        
        return Agent(
            config=self.agents_config["senior_software_developer_and_code_generator"],
            
            
            tools=[				CodeAnalysisTool()],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            max_execution_time=None,
            llm=LLM(
                model="openai/gpt-4o-mini",
                temperature=0.7,
            ),
            
        )
    

    
    @task
    def generate_code_based_on_prompt(self) -> Task:
        return Task(
            config=self.tasks_config["generate_code_based_on_prompt"],
            markdown=False,
            
            
        )
    

    @crew
    def crew(self) -> Crew:
        """Creates the AiCodeGenerator crew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )

    def _load_response_format(self, name):
        with open(os.path.join(self.base_directory, "config", f"{name}.json")) as f:
            json_schema = json.loads(f.read())

        return SchemaConverter.build(json_schema)
