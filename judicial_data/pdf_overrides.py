def override_pdf_entry(entry):
    if 'Circuit' in entry and entry['Circuit'] == 'PL 107-273':
        return {
            'Circuit': 'NC-W',
            'Vacancy Created By': 'PL 107-273',
            'Reason': 'New Position',
            'Vacancy Date': '7/15/03',
            'Nominee': 'Conrad, Robert Jr.',
            'Nomination': '4/28/03',
        }
    return entry