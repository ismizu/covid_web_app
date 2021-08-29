import pickle
import base64
import streamlit as st
from datetime import date
import plotly.graph_objects as go
from plotly.subplots import make_subplots

#Set initial app layout
st.set_page_config(layout = 'wide', initial_sidebar_state = 'collapsed')

#Set title
st.title('COVID-19: Vaccination Rate Simulator')
st.markdown('> ### Select a state from the dropdown menu to begin.')
st.markdown('<font size="2"><i>Data Update Currently In Progress</i></font>',
            unsafe_allow_html = True)

#----- Sidebar discussing errors -----#
st.sidebar.markdown('''The following models require additional tuning:
- Hawaii
- Maine
- Minnesota
- New Mexico
- Ohio
- Oregon
- South Dakota
- Virginia
- Wisconsin
''')
sidebar_problem = st.sidebar.beta_expander('What\'s wrong?')
sidebar_problem.markdown('''Currently, the models do not accurately alter hospitalizations \
and fatalities as the vaccination rate changes.

#### Why does this happen?

Facebook's Prophet utilizes two powerful effects to increase forecast accuracy. They are:

1. Changepoint Range

2. Changepoint Prior Scale

A changepoint is when Prophet identifies a change in the trend over time.

Changepoint range indicates how far into the data you wish to account for changepoints.

Changepoint prior scale indicates how sensitive you want the model to be when looking for changepoints.

The predictions utilize vaccination rates to predict the target variables (hospitalizations and fatalities). \
Thus, if the changepoint range and sensitivity detect a changepoint during an upward trend, \
the trend will be set to an increase in the target variables. What the model will then believe is \
that the increasing vaccination rate is to blame.''')

sidebar_problem_fix = st.sidebar.beta_expander('What is being done to fix this?')
sidebar_problem_fix.markdown('''Currently, the following fixes are in the works:

1. Adjust the changepoint variables:
>- Adjustments can be made to help the model capture the general trend. \
As opposed to capturing many smaller trends.

2. Large increases in hospitalizations and fatalities can be linked to specific events \
(Such as the emergence of the delta strain)
>- The dates of these events can be entered into Facebook Prophet to help it \
identify the overall trend by understanding where anomalies are.''')

#Get days since first US COVID case
current_date = date.today()
covid_first_case = date(2020, 1, 19)
days_since = current_date - covid_first_case

st.sidebar.markdown(f'''>One of the biggest problems with the model falls to available data per state.


The first confirmed case of COVID-19 in the US was on January 19th, 2020. This means that \
the max collectable data would be {days_since.days}.

For this project, weekly data is used. \
This means that each state can only have a max of {round(days_since.days/7)} data points.


For machine learning models, this is incredibly low and affects its ability to accurately \
predict the future.''')

#----- Set local image as background -----#
# Currently unused #
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(png_file):
    bin_str = get_base64(png_file)
    page_bg_img = '''
    <style>
    .stApp {
      background-image: url("data:image/png;base64,%s");
      background-size: cover;
    }
    </style>
    ''' % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)

set_background('images/blank.png')

#----- Set max width -----#
st.markdown(
        """
<style>
    .reportview-container .main .block-container{
        max-width: 1440px;
    }
</style>
""",
        unsafe_allow_html=True,
    )


#----- Visualizations -----#

#Load in states data
load_states_dict = open('pickled_data/general_data/states.pickle','rb')
states = pickle.load(load_states_dict)
load_states_dict.close()

#Create selection box
selection_box = st.selectbox('State: ', list(states.values()))

#Function to open figure for selection
def widget_fig(state_value):
    
    state_value = [x for x,y in list(zip(states.keys(), states.values())) if y == selection_box][0]
    
    load_graph = open(f'pickled_data/graphs_pickled/{state_value}_graph_dict.pickle','rb')
    fig = pickle.load(load_graph)
    load_graph.close()

    return fig

#Render plotly figure
st.plotly_chart(widget_fig(selection_box), use_container_width = True)

#----- Component Plots -----#

#Function to retrieve correct component plots
def component_plot_path(state_value):

    state_value = [x for x,y in list(zip(states.keys(), states.values())) if y == selection_box][0]

    deaths_image_path = f'pickled_data/forecast_plots/{state_value}_deaths_forecast_plot.jpg'
    hosp_image_path = f'pickled_data/forecast_plots/{state_value}_hosp_forecast_plot.jpg'

    return deaths_image_path, hosp_image_path, state_value

st.markdown('<font size="2"><i>Select the arrow in the upper left hand corner to view current bugs/fixes</i></font>',
            unsafe_allow_html = True)

#Toggle expander for component plots
show_more = st.beta_expander('How does this work?')

show_more.markdown('''Below, you can view the components that went into making the baseline predictions.

- The y-axis shows the number of fatalities or hospitalizations.
- The x-axis shows the date.

### Plots Defined

> Note: Exogenous variable means any extra information added to the model to help it make predictions

1. **Trend** - This is the general trend that the model forecasts sans exogenous variables
2. **Holidays** - Outliers obtained from Reich Lab were input into Prophet via the Holidays functionality. \
Any change indicated here means the model recognized a change in the trend and changed the prediction as a result. \
Not all states contain outliers and thus, will not contain this plot.
3. **Extra Regressors** - Extra regressors are the exogenous variables. In this case, the percent of the population \
that is vaccinated. This plot show how the model's fatality and hospitalization predictions are \
altered as a result of vaccination rates.''')

#Split expander into two columns
col1, col2 = show_more.beta_columns(2)

extra_components = component_plot_path(selection_box)

#Attach fbprophet's component plots to columns
col1.header(f'{extra_components[2]} Fatality Forecast Plot')
col1.image(extra_components[0], use_column_width = True)

col2.header(f'{extra_components[2]} Hospitalization Forecast Plot')
col2.image(extra_components[1], use_column_width = True)

#Additional Notes
more_notes = st.beta_expander('Important Assumptions')

more_notes.markdown('''The models for project make a few important assumptions that are noted below:

1. The model assumes that, when increasing the vaccination rate, that many vaccines were actually available.
>Vaccines in the US were in short supply for some time. Alterations to the vaccination rates do not cap at supply limits
2. The model assumes that all events that did happen, would still happen exactly as they did regardless of changes to \
vaccination rates.
>For example, some super spreader events may never have happened if vaccination rates were different. \
In addition, the US was successfully vaccinating individuals when the Delta strain emerged. \
What might things look like right now if the vaccine had not been available when the strain emerged? \
The model is incapable of predicting what never happened and can only alter existing trends. Thus, \
any changes it creates to hospitalizations and fatalities are based on the idea that whatever did happen \
still happened.
3. The model assumes that the entirety of a state\'s population can be vaccinated.
>There are individuals who rely on herd immunity as they, for genuine medical reasons, \
cannot receive vaccinations. Although an extremely low percentage of the population, \
it still means that a vaccination rate of 100% is not possible. For more information \
on who cannot receive vaccinations, please refer to [this CDC resource](https://www.cdc.gov/vaccines/vpd/should-not-vacc.html).
''')