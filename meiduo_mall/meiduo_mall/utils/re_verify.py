import re


def re_verification(**kwargs):
    results = []

    if 'username' in kwargs:
        results.append(re.match(r'^[a-zA-Z0-9_-]{5,20}$', kwargs['username']))

    if 'password' in kwargs:
        results.append(re.match(r'^[0-9A-Za-z]{8,20}$', kwargs['password']))

    if 'mobile' in kwargs:
        results.append(re.match(r'^1[345789]\d{9}$', kwargs['mobile']))

    if 'email' in kwargs:
        results.append(re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', kwargs['email']))

    return all(results)


if __name__ == '__main__':
    print(re_verification(email='freedom@america.us'))
