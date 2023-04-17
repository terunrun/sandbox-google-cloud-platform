select
    st.name as name,
    st.description as description,
    current_date('Asia/Tokyo') as day
from
    `import.sample_table` as st
