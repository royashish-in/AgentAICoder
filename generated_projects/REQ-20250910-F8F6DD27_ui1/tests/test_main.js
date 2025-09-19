describe('App component', () => {
  test('renders correctly', () => {
    const wrapper = shallow(<App />);
    expect(wrapper.find('div').length).toBe(1);
  });

  test('catches error and displays it', () => {
    const error = new Error('Test error');
    const wrapper = mount(<App />, { wrappingComponent: props => <div>{props.children}</div> });
    wrapper.setProps({ error });
    expect(wrapper.text()).toContain('Error rendering component:');
  });

  test('returns default value when error occurs', () => {
    const error = new Error('Test error');
    const wrapper = mount(<App />, { wrappingComponent: props => <div>{props.children}</div> });
    wrapper.setProps({ error });
    expect(wrapper.find('div').length).toBe(1);
  });
});